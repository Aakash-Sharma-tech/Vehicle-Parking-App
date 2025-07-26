from models.database import get_db_connection
from datetime import datetime
import math

class ReservationModel:
    
    @staticmethod
    def create_reservation(user_id, spot_id, vehicle_number, cost_per_hour):
        """Create a new reservation"""
        conn = get_db_connection()
        
        try:
            # Create reservation
            parking_timestamp = datetime.now().isoformat()
            conn.execute(
                'INSERT INTO reservations (user_id, spot_id, vehicle_number, parking_timestamp, cost_per_hour, status) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, spot_id, vehicle_number, parking_timestamp, cost_per_hour, 'active')
            )
            
            # Update spot status to occupied
            conn.execute(
                'UPDATE parking_spots SET status = "O" WHERE id = ?',
                (spot_id,)
            )
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    @staticmethod
    def get_user_active_reservations(user_id):
        """Get all active reservations for a user"""
        conn = get_db_connection()
        reservations = conn.execute('''
            SELECT 
                r.*,
                pl.location_name,
                pl.address,
                ps.id as spot_number
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE r.user_id = ? AND r.status = 'active'
            ORDER BY r.parking_timestamp DESC
        ''', (user_id,)).fetchall()
        conn.close()
        return [dict(reservation) for reservation in reservations]
    
    @staticmethod
    def get_user_reservation_history(user_id):
        """Get all reservations (active and completed) for a user"""
        conn = get_db_connection()
        reservations = conn.execute('''
            SELECT 
                r.*,
                pl.location_name,
                pl.address,
                ps.id as spot_number
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE r.user_id = ?
            ORDER BY r.parking_timestamp DESC
        ''', (user_id,)).fetchall()
        conn.close()
        return [dict(reservation) for reservation in reservations]
    
    @staticmethod
    def release_reservation(reservation_id, user_id):
        """Release a reservation and calculate total cost"""
        conn = get_db_connection()
        
        try:
            # Get reservation details
            reservation = conn.execute(
                'SELECT * FROM reservations WHERE id = ? AND user_id = ? AND status = "active"',
                (reservation_id, user_id)
            ).fetchone()
            
            if not reservation:
                conn.close()
                return False
            
            # Calculate total cost
            parking_time = datetime.fromisoformat(reservation['parking_timestamp'])
            leaving_time = datetime.now()
            duration_hours = (leaving_time - parking_time).total_seconds() / 3600
            total_cost = math.ceil(duration_hours) * reservation['cost_per_hour']
            
            # Update reservation
            conn.execute(
                'UPDATE reservations SET leaving_timestamp = ?, total_cost = ?, status = "completed" WHERE id = ?',
                (leaving_time.isoformat(), total_cost, reservation_id)
            )
            
            # Update spot status to available
            conn.execute(
                'UPDATE parking_spots SET status = "A" WHERE id = ?',
                (reservation['spot_id'],)
            )
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    @staticmethod
    def get_all_reservations():
        """Get all reservations for admin view"""
        conn = get_db_connection()
        reservations = conn.execute('''
            SELECT 
                r.*,
                u.name as user_name,
                u.email as user_email,
                pl.location_name,
                ps.id as spot_number
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            ORDER BY r.parking_timestamp DESC
        ''').fetchall()
        conn.close()
        return [dict(reservation) for reservation in reservations]