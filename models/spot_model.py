from models.database import get_db_connection

class SpotModel:
    
    @staticmethod
    def get_available_spots_by_lot(lot_id):
        """Get all available spots for a specific lot"""
        conn = get_db_connection()
        spots = conn.execute(
            'SELECT * FROM parking_spots WHERE lot_id = ? AND status = "A"',
            (lot_id,)
        ).fetchall()
        conn.close()
        return [dict(spot) for spot in spots]
    
    @staticmethod
    def get_spot_by_id(spot_id):
        """Get spot by ID"""
        conn = get_db_connection()
        spot = conn.execute(
            'SELECT * FROM parking_spots WHERE id = ?',
            (spot_id,)
        ).fetchone()
        conn.close()
        return dict(spot) if spot else None
    
    @staticmethod
    def update_spot_status(spot_id, status):
        """Update spot status"""
        conn = get_db_connection()
        conn.execute(
            'UPDATE parking_spots SET status = ? WHERE id = ?',
            (status, spot_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_spots_by_lot_with_details(lot_id):
        """Get all spots for a lot with reservation details"""
        conn = get_db_connection()
        spots = conn.execute('''
            SELECT 
                ps.*,
                r.vehicle_number,
                r.parking_timestamp,
                u.name as user_name
            FROM parking_spots ps
            LEFT JOIN reservations r ON ps.id = r.spot_id AND r.status = 'active'
            LEFT JOIN users u ON r.user_id = u.id
            WHERE ps.lot_id = ?
            ORDER BY ps.id
        ''', (lot_id,)).fetchall()
        conn.close()
        return [dict(spot) for spot in spots]