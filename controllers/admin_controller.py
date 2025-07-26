from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.admin_model import AdminModel
from models.lot_model import LotModel
from models.user_model import UserModel
from models.reservation_model import ReservationModel
from models.spot_model import SpotModel

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session.get('is_admin'):
            flash('Admin access required!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = AdminModel.get_dashboard_stats()
    lots = LotModel.get_all_lots()
    return render_template('admin_dashboard.html', stats=stats, lots=lots)

@admin_bp.route('/add_lot', methods=['GET', 'POST'])
@admin_required
def add_lot():
    if request.method == 'POST':
        location_name = request.form['location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])
        
        if LotModel.create_lot(location_name, price, address, pin_code, max_spots):
            flash('Parking lot created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        flash('Failed to create parking lot!', 'error')
    
    return render_template('add_parking_lot.html')

@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = LotModel.get_lot_by_id(lot_id)
    if not lot:
        flash('Parking lot not found!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        location_name = request.form['location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])
        
        if LotModel.update_lot(lot_id, location_name, price, address, pin_code, max_spots):
            flash('Parking lot updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        flash('Failed to update parking lot!', 'error')
    
    return render_template('add_parking_lot.html', lot=lot, edit_mode=True)

@admin_bp.route('/delete_lot/<int:lot_id>')
@admin_required
def delete_lot(lot_id):
    if LotModel.delete_lot(lot_id):
        flash('Parking lot deleted successfully!', 'success')
    else:
        flash('Failed to delete parking lot!', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/view_lot/<int:lot_id>')
@admin_required
def view_lot(lot_id):
    lot = LotModel.get_lot_by_id(lot_id)
    if not lot:
        flash('Parking lot not found!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    spots = SpotModel.get_spots_by_lot_with_details(lot_id)
    return render_template('view_lot_details.html', lot=lot, spots=spots)

@admin_bp.route('/users')
@admin_required
def view_users():
    users = UserModel.get_all_users()
    return render_template('view_users.html', users=users)

@admin_bp.route('/reservations')
@admin_required
def view_reservations():
    reservations = ReservationModel.get_all_reservations()
    return render_template('view_reservations.html', reservations=reservations)