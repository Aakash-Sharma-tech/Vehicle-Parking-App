from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.models import ParkingLot, ParkingSpot, Reservation, User
from models.database import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    lots = ParkingLot.get_all()
    reservations = Reservation.get_active_reservations()
    users = User.get_all()
    
    # Get statistics
    conn = get_db_connection()
    stats = {
        'total_lots': len(lots),
        'total_users': len(users),
        'active_reservations': len(reservations),
        'total_spots': conn.execute('SELECT COUNT(*) FROM parking_spots').fetchone()[0],
        'occupied_spots': conn.execute('SELECT COUNT(*) FROM parking_spots WHERE status = "O"').fetchone()[0],
        'total_revenue': conn.execute('SELECT COALESCE(SUM(total_cost), 0) FROM reservations WHERE status = "completed"').fetchone()[0]
    }
    conn.close()
    
    return render_template('admin_dashboard.html', lots=lots, reservations=reservations, users=users, stats=stats)

@admin_bp.route('/parking-lots')
@admin_required
def parking_lots():
    lots = ParkingLot.get_all()
    return render_template('admin_parking_lots.html', lots=lots)

@admin_bp.route('/parking-lots/create', methods=['GET', 'POST'])
@admin_required
def create_lot():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])
        
        if ParkingLot.create(name, price, address, pin_code, max_spots):
            flash('Parking lot created successfully!', 'success')
            return redirect(url_for('admin.parking_lots'))
        else:
            flash('Error creating parking lot!', 'danger')
    
    return render_template('admin_create_lot.html')

@admin_bp.route('/parking-lots/edit/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.get_by_id(lot_id)
    if not lot:
        flash('Parking lot not found!', 'danger')
        return redirect(url_for('admin.parking_lots'))
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])
        
        if ParkingLot.update(lot_id, name, price, address, pin_code, max_spots):
            flash('Parking lot updated successfully!', 'success')
            return redirect(url_for('admin.parking_lots'))
        else:
            flash('Error updating parking lot!', 'danger')
    
    return render_template('admin_edit_lot.html', lot=lot)

@admin_bp.route('/parking-lots/delete/<int:lot_id>', methods=['POST'])
@admin_required
def delete_lot(lot_id):
    success, message = ParkingLot.delete(lot_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.parking_lots'))

@admin_bp.route('/parking-spots')
@admin_required
def parking_spots():
    spots = ParkingSpot.get_all_spots()
    return render_template('admin_parking_spots.html', spots=spots)

@admin_bp.route('/reservations')
@admin_required
def reservations():
    all_reservations = Reservation.get_all_reservations()
    return render_template('admin_reservations.html', reservations=all_reservations)

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.get_all()
    return render_template('admin_users.html', users=all_users)

@admin_bp.route('/api/dashboard-stats')
@admin_required
def dashboard_stats():
    conn = get_db_connection()
    
    # Get monthly revenue data
    monthly_revenue = conn.execute('''
        SELECT strftime('%Y-%m', parking_timestamp) as month,
               SUM(total_cost) as revenue
        FROM reservations 
        WHERE status = 'completed' AND parking_timestamp >= date('now', '-12 months')
        GROUP BY month
        ORDER BY month
    ''').fetchall()
    
    # Get lot utilization data
    lot_utilization = conn.execute('''
        SELECT pl.name,
               COUNT(CASE WHEN ps.status = 'O' THEN 1 END) as occupied,
               COUNT(ps.id) as total
        FROM parking_lots pl
        LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
        GROUP BY pl.id, pl.name
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'monthly_revenue': [{'month': row['month'], 'revenue': row['revenue']} for row in monthly_revenue],
        'lot_utilization': [{'name': row['name'], 'occupied': row['occupied'], 'total': row['total']} for row in lot_utilization]
    })