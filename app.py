from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from models.database import init_db
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parkinglots', methods=['GET'])
def api_parking_lots():
    """REST API endpoint for parking lots"""
    from models.database import get_db_connection
    
    conn = get_db_connection()
    lots = conn.execute('''
        SELECT pl.*, 
               COUNT(CASE WHEN ps.status = 'A' THEN 1 END) as available_spots,
               COUNT(ps.id) as total_spots
        FROM parking_lots pl
        LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
        GROUP BY pl.id
    ''').fetchall()
    conn.close()
    
    return jsonify([{
        'id': lot['id'],
        'name': lot['name'],
        'price': lot['price'],
        'address': lot['address'],
        'pin_code': lot['pin_code'],
        'max_spots': lot['max_spots'],
        'available_spots': lot['available_spots'],
        'total_spots': lot['total_spots']
    } for lot in lots])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)