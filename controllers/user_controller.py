from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.lot_model import LotModel
from models.spot_model import SpotModel
from models.reservation_model import ReservationModel

user_bp = Blueprint('user', __name__, url_prefix='/user')

def login_required(f):
    """Decorator to require user authentication"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login to continue!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user']['id']
    active_reservations = ReservationModel.get_user_active_reservations(user_id)
    lots = LotModel.get_all_lots()
    return render_template('user_dashboard.html', 
                         active_reservations=active_reservations, 
                         lots=lots)

@user_bp.route('/book_spot/<int:lot_id>', methods=['POST'])
@login_required
def book_spot(lot_id):
    user_id = session['user']['id']
    vehicle_number = request.form['vehicle_number']
    
    # Get lot details
    lot = LotModel.get_lot_by_id(lot_id)
    if not lot:
        flash('Parking lot not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get first available spot
    available_spots = SpotModel.get_available_spots_by_lot(lot_id)
    if not available_spots:
        flash('No available spots in this lot!', 'error')
        return redirect(url_for('user.dashboard'))
    
    spot_id = available_spots[0]['id']
    
    if ReservationModel.create_reservation(user_id, spot_id, vehicle_number, lot['price']):
        flash('Parking spot booked successfully!', 'success')
    else:
        flash('Failed to book parking spot!', 'error')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/release_spot/<int:reservation_id>')
@login_required
def release_spot(reservation_id):
    user_id = session['user']['id']
    
    if ReservationModel.release_reservation(reservation_id, user_id):
        flash('Parking spot released successfully!', 'success')
    else:
        flash('Failed to release parking spot!', 'error')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/history')
@login_required
def reservation_history():
    user_id = session['user']['id']
    reservations = ReservationModel.get_user_reservation_history(user_id)
    return render_template('reservation_history.html', reservations=reservations)