from models import db
from datetime import datetime

class ReservationModel(db.Model):
    """Reservation model for parking bookings"""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, parking_spot_id, vehicle_number):
        self.user_id = user_id
        self.parking_spot_id = parking_spot_id
        self.vehicle_number = vehicle_number
    
    def calculate_cost(self, hourly_rate):
        """Calculate total cost based on duration and hourly rate"""
        if self.check_out_time and self.check_in_time:
            duration = self.check_out_time - self.check_in_time
            hours = max(1, duration.total_seconds() / 3600)  # Minimum 1 hour charge
            return round(hours * hourly_rate, 2)
        return 0
    
    def get_duration(self):
        """Get parking duration as string"""
        if self.check_out_time and self.check_in_time:
            duration = self.check_out_time - self.check_in_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        elif self.check_in_time:
            duration = datetime.utcnow() - self.check_in_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m (ongoing)"
        return "N/A"
    
    def __repr__(self):
        return f'<Reservation {self.id} - {self.vehicle_number}>'