from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, UserModel, ParkingLotModel, ParkingSpotModel, ReservationModel
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    """Decorator to require user authentication"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('is_admin'):
            flash('User access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@user_required
def dashboard():
    """User dashboard"""
    user_id = session.get('user_id')
    user = UserModel.query.get(user_id)
    
    # Get user's active reservations
    active_reservations = ReservationModel.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()
    
    # Get recent reservations
    recent_reservations = ReservationModel.query.filter_by(
        user_id=user_id
    ).order_by(ReservationModel.created_at.desc()).limit(5).all()
    
    return render_template('user/dashboard.html',
                         user=user,
                         active_reservations=active_reservations,
                         recent_reservations=recent_reservations)

@user_bp.route('/book-parking')
@user_required
def book_parking():
    """Select parking lot to book"""
    lots = ParkingLotModel.query.filter_by(is_active=True).all()
    return render_template('user/book_parking.html', lots=lots)

@user_bp.route('/book-parking/<int:lot_id>', methods=['GET', 'POST'])
@user_required
def book_spot(lot_id):
    """Book a specific spot in parking lot"""
    lot = ParkingLotModel.query.get_or_404(lot_id)
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        
        if not vehicle_number:
            flash('Please enter vehicle number', 'error')
            return redirect(url_for('user.book_spot', lot_id=lot_id))
        
        # Find first available spot
        available_spot = ParkingSpotModel.query.filter_by(
            parking_lot_id=lot_id,
            is_available=True
        ).first()
        
        if not available_spot:
            flash('No available spots in this parking lot', 'error')
            return redirect(url_for('user.book_parking'))
        
        try:
            # Create reservation
            reservation = ReservationModel(
                user_id=user_id,
                parking_spot_id=available_spot.id,
                vehicle_number=vehicle_number.upper()
            )
            db.session.add(reservation)
            
            # Mark spot as occupied
            available_spot.is_available = False
            
            db.session.commit()
            flash(f'Parking spot {available_spot.spot_number} booked successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error booking parking spot', 'error')
    
    available_count = ParkingSpotModel.query.filter_by(
        parking_lot_id=lot_id,
        is_available=True
    ).count()
    
    return render_template('user/book_spot.html', lot=lot, available_count=available_count)

@user_bp.route('/release-parking/<int:reservation_id>')
@user_required
def release_parking(reservation_id):
    """Release/vacate a parking spot"""
    user_id = session.get('user_id')
    reservation = ReservationModel.query.filter_by(
        id=reservation_id,
        user_id=user_id,
        is_active=True
    ).first_or_404()
    
    try:
        # Calculate cost and update reservation
        parking_lot = reservation.parking_spot.parking_lot
        reservation.check_out_time = datetime.utcnow()
        reservation.total_cost = reservation.calculate_cost(parking_lot.price_per_hour)
        reservation.is_active = False
        
        # Mark spot as available
        reservation.parking_spot.is_available = True
        
        db.session.commit()
        flash(f'Parking released. Total cost: ₹{reservation.total_cost}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error releasing parking spot', 'error')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/history')
@user_required
def history():
    """View parking history"""
    user_id = session.get('user_id')
    reservations = ReservationModel.query.filter_by(
        user_id=user_id
    ).order_by(ReservationModel.created_at.desc()).all()
    
    return render_template('user/history.html', reservations=reservations)

@user_bp.route('/api/user-chart-data')
@user_required
def user_chart_data():
    """API endpoint for user's chart data"""
    user_id = session.get('user_id')
    
    # Monthly spending data
    reservations = ReservationModel.query.filter_by(
        user_id=user_id
    ).filter(ReservationModel.total_cost.isnot(None)).all()
    
    monthly_data = {}
    for reservation in reservations:
        if reservation.check_out_time:
            month = reservation.check_out_time.strftime('%Y-%m')
            monthly_data[month] = monthly_data.get(month, 0) + (reservation.total_cost or 0)
    
    months = list(monthly_data.keys())
    spending = list(monthly_data.values())
    
    return jsonify({
        'months': months,
        'spending': spending
    })