from flask import Flask, render_template, redirect, url_for, session
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
from models import db
db.init_app(app)

# Import models after db initialization
from models import AdminModel, UserModel, ParkingLotModel, ParkingSpotModel, ReservationModel

# Import routes
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    """Home page - redirect based on session"""
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return render_template('index.html')

def create_admin_user():
    """Create default admin user if doesn't exist"""
    admin = AdminModel.query.filter_by(username=Config.ADMIN_USERNAME).first()
    if not admin:
        admin = AdminModel(
            username=Config.ADMIN_USERNAME,
            password=Config.ADMIN_PASSWORD
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created successfully!")

def init_database():
    """Initialize database and create tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create default admin user
        create_admin_user()

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists('parking_app.db'):
        init_database()
    
    # Run the application
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
