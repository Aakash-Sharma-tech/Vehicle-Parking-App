from models import db
from datetime import datetime

class ParkingSpotModel(db.Model):
    """Parking spot model"""
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with reservations
    reservations = db.relationship('ReservationModel', backref='parking_spot', lazy=True)
    
    def __init__(self, spot_number, parking_lot_id):
        self.spot_number = spot_number
        self.parking_lot_id = parking_lot_id
    
    def get_current_reservation(self):
        """Get current active reservation for this spot"""
        from models.reservation import ReservationModel
        return ReservationModel.query.filter_by(
            parking_spot_id=self.id,
            is_active=True
        ).first()
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number}>'