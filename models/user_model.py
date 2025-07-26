from models.database import get_db_connection
import hashlib

class UserModel:
    
    @staticmethod
    def create_user(name, email, password):
        """Create a new user"""
        conn = get_db_connection()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user login"""
        conn = get_db_connection()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hashed_password)
        ).fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return [dict(user) for user in users]
    
    @staticmethod
    def email_exists(email):
        """Check if email already exists"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()
        return user is not None