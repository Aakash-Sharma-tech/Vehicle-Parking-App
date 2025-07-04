import sqlite3
import os
from datetime import datetime

DATABASE = 'parking_app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            address TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            max_spots INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            spot_number INTEGER NOT NULL,
            status TEXT CHECK(status IN ('A', 'O')) DEFAULT 'A',
            FOREIGN KEY (lot_id) REFERENCES parking_lots (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parking_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leaving_timestamp TIMESTAMP,
            cost_per_hour REAL,
            total_cost REAL,
            status TEXT CHECK(status IN ('active', 'completed', 'cancelled')) DEFAULT 'active',
            FOREIGN KEY (spot_id) REFERENCES parking_spots (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_parking_spots_lot_id ON parking_spots(lot_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reservations_spot_id ON reservations(spot_id)')
    
    conn.commit()
    conn.close()
    
    # Seed dummy data
    seed_data()

def seed_data():
    """Seed the database with dummy data"""
    conn = get_db_connection()
    
    # Check if data already exists
    existing_lots = conn.execute('SELECT COUNT(*) FROM parking_lots').fetchone()[0]
    if existing_lots > 0:
        conn.close()
        return
    
    # Insert dummy parking lots
    lots = [
        ('Downtown Plaza', 25.0, '123 Main St, Downtown', '12345', 50),
        ('Mall Parking', 15.0, '456 Shopping Ave, Mall District', '54321', 100),
        ('Airport Parking', 35.0, '789 Airport Rd, Terminal 1', '67890', 200),
        ('City Center', 20.0, '321 Business St, City Center', '98765', 75)
    ]
    
    for lot in lots:
        conn.execute('''
            INSERT INTO parking_lots (name, price, address, pin_code, max_spots)
            VALUES (?, ?, ?, ?, ?)
        ''', lot)
    
    conn.commit()
    
    # Generate parking spots for each lot
    lots_data = conn.execute('SELECT id, max_spots FROM parking_lots').fetchall()
    
    for lot in lots_data:
        for spot_num in range(1, lot['max_spots'] + 1):
            conn.execute('''
                INSERT INTO parking_spots (lot_id, spot_number, status)
                VALUES (?, ?, 'A')
            ''', (lot['id'], spot_num))
    
    # Insert dummy user
    conn.execute('''
        INSERT INTO users (username, password, email, phone)
        VALUES ('demo_user', 'password123', 'demo@example.com', '+1234567890')
    ''')
    
    conn.commit()
    conn.close()