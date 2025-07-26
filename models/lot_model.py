from models.database import get_db_connection

class LotModel:
    
    @staticmethod
    def create_lot(location_name, price, address, pin_code, max_spots):
        """Create a new parking lot and auto-generate spots"""
        conn = get_db_connection()
        
        try:
            # Insert the parking lot
            cursor = conn.execute(
                'INSERT INTO parking_lots (location_name, price, address, pin_code, max_spots) VALUES (?, ?, ?, ?, ?)',
                (location_name, price, address, pin_code, max_spots)
            )
            lot_id = cursor.lastrowid
            
            # Auto-create parking spots
            for i in range(max_spots):
                conn.execute(
                    'INSERT INTO parking_spots (lot_id, status) VALUES (?, ?)',
                    (lot_id, 'A')
                )
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    @staticmethod
    def get_all_lots():
        """Get all parking lots with spot counts"""
        conn = get_db_connection()
        
        lots = conn.execute('''
            SELECT 
                pl.*,
                COUNT(ps.id) as total_spots,
                SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available_spots,
                SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots
            FROM parking_lots pl
            LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
            GROUP BY pl.id
        ''').fetchall()
        
        conn.close()
        return [dict(lot) for lot in lots]
    
    @staticmethod
    def get_lot_by_id(lot_id):
        """Get parking lot by ID"""
        conn = get_db_connection()
        lot = conn.execute(
            'SELECT * FROM parking_lots WHERE id = ?',
            (lot_id,)
        ).fetchone()
        conn.close()
        return dict(lot) if lot else None
    
    @staticmethod
    def update_lot(lot_id, location_name, price, address, pin_code, max_spots):
        """Update parking lot and adjust spots if needed"""
        conn = get_db_connection()
        
        try:
            # Get current max_spots
            current_lot = conn.execute(
                'SELECT max_spots FROM parking_lots WHERE id = ?',
                (lot_id,)
            ).fetchone()
            
            current_spots = current_lot['max_spots'] if current_lot else 0
            
            # Update the lot
            conn.execute(
                'UPDATE parking_lots SET location_name = ?, price = ?, address = ?, pin_code = ?, max_spots = ? WHERE id = ?',
                (location_name, price, address, pin_code, max_spots, lot_id)
            )
            
            # Adjust spots if needed
            if max_spots > current_spots:
                # Add new spots
                for i in range(max_spots - current_spots):
                    conn.execute(
                        'INSERT INTO parking_spots (lot_id, status) VALUES (?, ?)',
                        (lot_id, 'A')
                    )
            elif max_spots < current_spots:
                # Remove excess spots (only available ones)
                spots_to_remove = current_spots - max_spots
                conn.execute(
                    'DELETE FROM parking_spots WHERE lot_id = ? AND status = "A" LIMIT ?',
                    (lot_id, spots_to_remove)
                )
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    @staticmethod
    def delete_lot(lot_id):
        """Delete parking lot and all associated spots/reservations"""
        conn = get_db_connection()
        
        try:
            # Delete reservations first
            conn.execute(
                'DELETE FROM reservations WHERE spot_id IN (SELECT id FROM parking_spots WHERE lot_id = ?)',
                (lot_id,)
            )
            
            # Delete spots
            conn.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
            
            # Delete lot
            conn.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False