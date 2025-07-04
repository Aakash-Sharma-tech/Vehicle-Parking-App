from models.database import get_db_connection
from datetime import datetime

class User:
    @staticmethod
    def create(username, password, email=None, phone=None):
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (username, password, email, phone)
                VALUES (?, ?, ?, ?)
            ''', (username, password, email, phone))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def authenticate(username, password):
        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
        conn.close()
        return users

class ParkingLot:
    @staticmethod
    def create(name, price, address, pin_code, max_spots):
        conn = get_db_connection()
        try:
            cursor = conn.execute('''
                INSERT INTO parking_lots (name, price, address, pin_code, max_spots)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, price, address, pin_code, max_spots))
            lot_id = cursor.lastrowid
            
            # Create parking spots
            for spot_num in range(1, max_spots + 1):
                conn.execute('''
                    INSERT INTO parking_spots (lot_id, spot_number, status)
                    VALUES (?, ?, 'A')
                ''', (lot_id, spot_num))
            
            conn.commit()
            return lot_id
        except Exception as e:
            print(f"Error creating parking lot: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        lots = conn.execute('''
            SELECT pl.*, 
                   COUNT(CASE WHEN ps.status = 'A' THEN 1 END) as available_spots,
                   COUNT(ps.id) as total_spots
            FROM parking_lots pl
            LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
            GROUP BY pl.id
            ORDER BY pl.created_at DESC
        ''').fetchall()
        conn.close()
        return lots
    
    @staticmethod
    def get_by_id(lot_id):
        conn = get_db_connection()
        lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
        conn.close()
        return lot
    
    @staticmethod
    def update(lot_id, name, price, address, pin_code, max_spots):
        conn = get_db_connection()
        try:
            # Update parking lot
            conn.execute('''
                UPDATE parking_lots 
                SET name = ?, price = ?, address = ?, pin_code = ?, max_spots = ?
                WHERE id = ?
            ''', (name, price, address, pin_code, max_spots, lot_id))
            
            # Get current spot count
            current_spots = conn.execute('''
                SELECT COUNT(*) FROM parking_spots WHERE lot_id = ?
            ''', (lot_id,)).fetchone()[0]
            
            # Adjust spots if needed
            if max_spots > current_spots:
                # Add more spots
                for spot_num in range(current_spots + 1, max_spots + 1):
                    conn.execute('''
                        INSERT INTO parking_spots (lot_id, spot_number, status)
                        VALUES (?, ?, 'A')
                    ''', (lot_id, spot_num))
            elif max_spots < current_spots:
                # Remove excess spots (only if they're available)
                conn.execute('''
                    DELETE FROM parking_spots 
                    WHERE lot_id = ? AND spot_number > ? AND status = 'A'
                ''', (lot_id, max_spots))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating parking lot: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(lot_id):
        conn = get_db_connection()
        try:
            # First check if there are active reservations
            active_reservations = conn.execute('''
                SELECT COUNT(*) FROM reservations r
                JOIN parking_spots ps ON r.spot_id = ps.id
                WHERE ps.lot_id = ? AND r.status = 'active'
            ''', (lot_id,)).fetchone()[0]
            
            if active_reservations > 0:
                return False, "Cannot delete parking lot with active reservations"
            
            # Delete reservations, spots, and then the lot
            conn.execute('''
                DELETE FROM reservations WHERE spot_id IN (
                    SELECT id FROM parking_spots WHERE lot_id = ?
                )
            ''', (lot_id,))
            
            conn.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
            conn.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
            
            conn.commit()
            return True, "Parking lot deleted successfully"
        except Exception as e:
            print(f"Error deleting parking lot: {e}")
            conn.rollback()
            return False, "Error deleting parking lot"
        finally:
            conn.close()

class ParkingSpot:
    @staticmethod
    def get_available_spots(lot_id):
        conn = get_db_connection()
        spots = conn.execute('''
            SELECT * FROM parking_spots 
            WHERE lot_id = ? AND status = 'A'
            ORDER BY spot_number
        ''', (lot_id,)).fetchall()
        conn.close()
        return spots
    
    @staticmethod
    def get_all_spots():
        conn = get_db_connection()
        spots = conn.execute('''
            SELECT ps.*, pl.name as lot_name
            FROM parking_spots ps
            JOIN parking_lots pl ON ps.lot_id = pl.id
            ORDER BY pl.name, ps.spot_number
        ''').fetchall()
        conn.close()
        return spots

class Reservation:
    @staticmethod
    def create(user_id, lot_id):
        conn = get_db_connection()
        try:
            # Get available spot
            spot = conn.execute('''
                SELECT id FROM parking_spots 
                WHERE lot_id = ? AND status = 'A'
                LIMIT 1
            ''', (lot_id,)).fetchone()
            
            if not spot:
                return None, "No available spots"
            
            # Get lot price
            lot = conn.execute('SELECT price FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
            
            # Mark spot as occupied
            conn.execute('''
                UPDATE parking_spots SET status = 'O' WHERE id = ?
            ''', (spot['id'],))
            
            # Create reservation
            cursor = conn.execute('''
                INSERT INTO reservations (spot_id, user_id, cost_per_hour, status)
                VALUES (?, ?, ?, 'active')
            ''', (spot['id'], user_id, lot['price']))
            
            reservation_id = cursor.lastrowid
            conn.commit()
            return reservation_id, "Parking spot reserved successfully"
        except Exception as e:
            print(f"Error creating reservation: {e}")
            conn.rollback()
            return None, "Error creating reservation"
        finally:
            conn.close()
    
    @staticmethod
    def release(reservation_id, user_id):
        conn = get_db_connection()
        try:
            # Get reservation details
            reservation = conn.execute('''
                SELECT r.*, ps.id as spot_id
                FROM reservations r
                JOIN parking_spots ps ON r.spot_id = ps.id
                WHERE r.id = ? AND r.user_id = ? AND r.status = 'active'
            ''', (reservation_id, user_id)).fetchone()
            
            if not reservation:
                return False, "Reservation not found or already completed"
            
            # Calculate total cost
            parking_time = datetime.now()
            parking_start = datetime.fromisoformat(reservation['parking_timestamp'])
            hours = (parking_time - parking_start).total_seconds() / 3600
            total_cost = max(hours * reservation['cost_per_hour'], reservation['cost_per_hour'])
            
            # Update reservation
            conn.execute('''
                UPDATE reservations 
                SET leaving_timestamp = ?, total_cost = ?, status = 'completed'
                WHERE id = ?
            ''', (parking_time, total_cost, reservation_id))
            
            # Mark spot as available
            conn.execute('''
                UPDATE parking_spots SET status = 'A' WHERE id = ?
            ''', (reservation['spot_id']))
            
            conn.commit()
            return True, f"Parking released. Total cost: ${total_cost:.2f}"
        except Exception as e:
            print(f"Error releasing reservation: {e}")
            conn.rollback()
            return False, "Error releasing parking spot"
        finally:
            conn.close()
    
    @staticmethod
    def get_user_reservations(user_id):
        conn = get_db_connection()
        reservations = conn.execute('''
            SELECT r.*, ps.spot_number, pl.name as lot_name, pl.address
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE r.user_id = ?
            ORDER BY r.parking_timestamp DESC
        ''', (user_id,)).fetchall()
        conn.close()
        return reservations
    
    @staticmethod
    def get_active_reservations():
        conn = get_db_connection()
        reservations = conn.execute('''
            SELECT r.*, ps.spot_number, pl.name as lot_name, u.username
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            JOIN users u ON r.user_id = u.id
            WHERE r.status = 'active'
            ORDER BY r.parking_timestamp DESC
        ''').fetchall()
        conn.close()
        return reservations
    
    @staticmethod
    def get_all_reservations():
        conn = get_db_connection()
        reservations = conn.execute('''
            SELECT r.*, ps.spot_number, pl.name as lot_name, u.username
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            JOIN users u ON r.user_id = u.id
            ORDER BY r.parking_timestamp DESC
        ''').fetchall()
        conn.close()
        return reservations