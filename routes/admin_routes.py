from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, AdminModel, UserModel, ParkingLotModel, ParkingSpotModel, ReservationModel
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    total_lots = ParkingLotModel.query.count()
    total_spots = ParkingSpotModel.query.count()
    total_users = UserModel.query.count()
    active_reservations = ReservationModel.query.filter_by(is_active=True).count()
    
    # Recent reservations
    recent_reservations = ReservationModel.query.order_by(
        ReservationModel.created_at.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_lots=total_lots,
                         total_spots=total_spots,
                         total_users=total_users,
                         active_reservations=active_reservations,
                         recent_reservations=recent_reservations)

@admin_bp.route('/parking-lots')
@admin_required
def parking_lots():
    """View all parking lots"""
    lots = ParkingLotModel.query.all()
    available = sum(lot.get_available_spots_count() for lot in lots)
    occupied = sum(lot.get_occupied_spots_count() for lot in lots)
    return render_template('admin/parking_lots.html', lots=lots, available=available, occupied=occupied)

@admin_bp.route('/parking-lots/add', methods=['GET', 'POST'])
@admin_required
def add_parking_lot():
    """Add new parking lot"""
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        price_per_hour = float(request.form.get('price_per_hour'))
        max_spots = int(request.form.get('max_spots'))
        
        try:
            # Create parking lot
            new_lot = ParkingLotModel(
                name=name,
                address=address,
                pincode=pincode,
                price_per_hour=price_per_hour,
                max_spots=max_spots
            )
            db.session.add(new_lot)
            db.session.flush()  # Get the ID
            
            # Create parking spots
            for i in range(1, max_spots + 1):
                spot = ParkingSpotModel(
                    spot_number=f"A{i:03d}",
                    parking_lot_id=new_lot.id
                )
                db.session.add(spot)
            
            db.session.commit()
            flash('Parking lot created successfully!', 'success')
            return redirect(url_for('admin.parking_lots'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating parking lot', 'error')
    
    return render_template('admin/add_parking_lot.html')

@admin_bp.route('/parking-lots/<int:lot_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_parking_lot(lot_id):
    """Edit existing parking lot and adjust spots if needed"""
    lot = ParkingLotModel.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.name = request.form.get('name')
        lot.address = request.form.get('address')
        lot.pincode = request.form.get('pincode')
        lot.price_per_hour = float(request.form.get('price_per_hour'))

        # ✅ New: Allow editing total spots
        new_total_spots = int(request.form.get('max_spots'))
        old_total_spots = lot.max_spots

        if new_total_spots != old_total_spots:
            lot.max_spots = new_total_spots
            adjust_parking_spots(lot, new_total_spots, old_total_spots)

        try:
            db.session.commit()
            flash('Parking lot updated successfully!', 'success')
            return redirect(url_for('admin.parking_lots'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating parking lot: {str(e)}', 'error')
    
    return render_template('admin/edit_parking_lot.html', lot=lot)

def adjust_parking_spots(lot, new_total, old_total):
    """Add or remove parking spots based on updated total"""
    if new_total > old_total:
        # Add new spots and make them available
        for spot_num in range(old_total + 1, new_total + 1):
            new_spot = ParkingSpotModel(
                spot_number=f"A{spot_num:03d}",
                parking_lot_id=lot.id,
                # is_available=True  # ✅ ensure availability
            )
            db.session.add(new_spot)

    elif new_total < old_total:
        # Remove excess spots (only if not occupied)
        spots_to_remove = ParkingSpotModel.query.filter(
            ParkingSpotModel.parking_lot_id == lot.id,
            ParkingSpotModel.spot_number > f"A{new_total:03d}"
        ).all()

        for spot in spots_to_remove:
            active_reservation = ReservationModel.query.filter_by(
                parking_spot_id=spot.id,
                is_active=True
            ).first()
            if not active_reservation:
                db.session.delete(spot)
            else:
                flash(f"Spot {spot.spot_number} is occupied and cannot be deleted.", "warning")

    # ✅ Ensure all existing free spots are marked available
    for spot in lot.spots:
        if not spot.get_current_reservation():  # no active booking
            spot.is_available = True



@admin_bp.route('/parking-lots/<int:lot_id>/delete')
@admin_required
def delete_parking_lot(lot_id):
    """Delete parking lot"""
    lot = ParkingLotModel.query.get_or_404(lot_id)
    try:
        # Delete all reservations associated with spots in this lot
        spots = ParkingSpotModel.query.filter_by(parking_lot_id=lot_id).all()
        for spot in spots:
            ReservationModel.query.filter_by(parking_spot_id=spot.id).delete()
        # Delete all spots in the lot
        ParkingSpotModel.query.filter_by(parking_lot_id=lot_id).delete()
        # Delete the lot itself
        db.session.delete(lot)
        db.session.commit()
        flash('Parking lot deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting parking lot: {e}', 'error')
    return redirect(url_for('admin.parking_lots'))

@admin_bp.route('/parking-lots/<int:lot_id>/spots')
@admin_required
def view_spots(lot_id):
    """View spots in a parking lot"""
    lot = ParkingLotModel.query.get_or_404(lot_id)
    spots = ParkingSpotModel.query.filter_by(parking_lot_id=lot_id).all()
    return render_template('admin/view_spots.html', lot=lot, spots=spots)

@admin_bp.route('/users')
@admin_required
def users():
    """View all users"""
    users = UserModel.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/reports')
@admin_required
def reports():
    """View reports and analytics"""
    # Get data for charts
    lots = ParkingLotModel.query.all()
    
    # Revenue data
    completed_reservations = ReservationModel.query.filter(
        ReservationModel.check_out_time.isnot(None)
    ).all()
    
    total_revenue = sum(r.total_cost or 0 for r in completed_reservations)
    
    return render_template('admin/reports.html',
                         lots=lots,
                         total_revenue=total_revenue,
                         completed_reservations=completed_reservations)

@admin_bp.route('/api/chart-data')
@admin_required
def chart_data():
    """API endpoint for chart data"""
    lots = ParkingLotModel.query.all()
    
    lot_names = []
    available_spots = []
    occupied_spots = []
    
    for lot in lots:
        lot_names.append(lot.name)
        available_spots.append(lot.get_available_spots_count())
        occupied_spots.append(lot.get_occupied_spots_count())
    
    return jsonify({
        'lot_names': lot_names,
        'available_spots': available_spots,
        'occupied_spots': occupied_spots
    })