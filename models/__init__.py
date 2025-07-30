# Models package initialization
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models after db initialization
from .admin import AdminModel
from .user import UserModel
from .parking_lot import ParkingLotModel
from .parking_spot import ParkingSpotModel
from .reservation import ReservationModel

__all__ = ['db', 'AdminModel', 'UserModel', 'ParkingLotModel', 'ParkingSpotModel', 'ReservationModel']