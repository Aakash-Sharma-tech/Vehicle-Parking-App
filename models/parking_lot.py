from models import db
from datetime import datetime

class ParkingLotModel(db.Model):
    """Parking lot model"""
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with parking spots
    spots = db.relationship('ParkingSpotModel', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, address, pincode, price_per_hour, max_spots):
        self.name = name
        self.address = address
        self.pincode = pincode
        self.price_per_hour = price_per_hour
        self.max_spots = max_spots
    
    def get_available_spots_count(self):
        """Get count of available spots"""
        return len([spot for spot in self.spots if spot.is_available])
    
    def get_occupied_spots_count(self):
        """Get count of occupied spots"""
        return len([spot for spot in self.spots if not spot.is_available])
    
    def __repr__(self):
        return f'<ParkingLot {self.name}>'