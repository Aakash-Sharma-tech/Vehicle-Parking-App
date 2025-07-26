# Vehicle Parking App

A complete multi-user parking management system built with Flask, featuring admin control and user booking functionality.

## Features

### Admin Features
- Login with hardcoded credentials (admin@example.com / admin123)
- Add, edit, and delete parking lots
- Auto-generation of parking spots based on lot capacity
- View all parking lots with real-time spot availability
- User management and reservation oversight
- Comprehensive dashboard with usage statistics

### User Features
- User registration and authentication
- View available parking lots
- Book multiple parking spots (no limit per user)
- Release active reservations with automatic cost calculation
- View reservation history with detailed cost breakdown
- Personal dashboard with active and past bookings

## Technology Stack

- **Backend**: Flask with SQLite database
- **Frontend**: Jinja2 templates with Bootstrap
- **Styling**: Custom CSS (no Tailwind, no JavaScript)
- **Authentication**: Flask sessions
- **Database**: SQLite with programmatic initialization

## Installation & Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the app at `http://localhost:5000`

## Database Structure

- **users**: User account information
- **parking_lots**: Parking lot details and pricing
- **parking_spots**: Individual parking spots with availability status
- **reservations**: Booking records with timestamps and cost calculation

## File Structure

```
/vehicle_parking_app
├── app.py                     # Main application file
├── models/                    # Database models
├── controllers/               # Route controllers
├── templates/                 # HTML templates
├── static/css/               # Custom CSS files
├── README.md
└── requirements.txt
```

## Default Admin Credentials

- **Email**: admin@example.com
- **Password**: admin123

## Features Highlights

- **Modular Architecture**: Clean separation of models, views, and controllers
- **Real-time Updates**: Dynamic spot availability and reservation status
- **Cost Calculation**: Automatic billing based on parking duration
- **Responsive Design**: Mobile-friendly interface
- **Data Integrity**: Proper foreign key relationships and constraints

The app is ready to run locally and provides a complete parking management solution for both administrators and end users.