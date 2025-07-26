from flask import Flask, redirect, url_for
from models.database import init_database
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    print("🚗 Vehicle Parking App Starting...")
    print("🔐 Admin Login: admin@example.com / admin123")
    print("👤 Register as user or use admin credentials")
    print("🌐 Access the app at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)