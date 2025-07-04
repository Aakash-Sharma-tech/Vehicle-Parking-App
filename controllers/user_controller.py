from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.models import ParkingLot, Reservation

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please login to access this page!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@user_required
def dashboard():
    user_id = session['user_id']
    reservations = Reservation.get_user_reservations(user_id)
    lots = ParkingLot.get_all()
    
    # Get active reservation
    active_reservation = None
    for reservation in reservations:
        if reservation['status'] == 'active':
            active_reservation = reservation
            break
    
    return render_template('user_dashboard.html', 
                         lots=lots, 
                         reservations=reservations,
                         active_reservation=active_reservation)

@user_bp.route('/book-parking', methods=['POST'])
@user_required
def book_parking():
    user_id = session['user_id']
    lot_id = request.form['lot_id']
    
    # Check if user already has an active reservation
    reservations = Reservation.get_user_reservations(user_id)
    for reservation in reservations:
        if reservation['status'] == 'active':
            flash('You already have an active parking reservation!', 'warning')
            return redirect(url_for('user.dashboard'))
    
    reservation_id, message = Reservation.create(user_id, lot_id)
    if reservation_id:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/release-parking/<int:reservation_id>', methods=['POST'])
@user_required
def release_parking(reservation_id):
    user_id = session['user_id']
    success, message = Reservation.release(reservation_id, user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/reservations')
@user_required
def reservations():
    user_id = session['user_id']
    user_reservations = Reservation.get_user_reservations(user_id)
    return render_template('user_reservations.html', reservations=user_reservations)