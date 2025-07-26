class AdminModel:
    
    @staticmethod
    def authenticate_admin(email, password):
        """Authenticate admin with hardcoded credentials"""
        if email == "admin@example.com" and password == "admin123":
            return {
                'id': 0,
                'name': 'Administrator',
                'email': 'admin@example.com',
                'role': 'admin'
            }
        return None
    
    @staticmethod
    def get_dashboard_stats():
        """Get admin dashboard statistics"""
        from models.database import get_db_connection
        
        conn = get_db_connection()
        
        # Get total lots
        total_lots = conn.execute('SELECT COUNT(*) as count FROM parking_lots').fetchone()['count']
        
        # Get total spots
        total_spots = conn.execute('SELECT COUNT(*) as count FROM parking_spots').fetchone()['count']
        
        # Get occupied spots
        occupied_spots = conn.execute('SELECT COUNT(*) as count FROM parking_spots WHERE status = "O"').fetchone()['count']
        
        # Get total users
        total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
        
        # Get active reservations
        active_reservations = conn.execute('SELECT COUNT(*) as count FROM reservations WHERE status = "active"').fetchone()['count']
        
        conn.close()
        
        return {
            'total_lots': total_lots,
            'total_spots': total_spots,
            'occupied_spots': occupied_spots,
            'available_spots': total_spots - occupied_spots,
            'total_users': total_users,
            'active_reservations': active_reservations
        }