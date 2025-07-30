# Vehicle Parking App - V1

A comprehensive multi-user web application for vehicle parking management built with Flask and SQLAlchemy.

## Features

### Admin Features
- Default admin login (username: `admin`, password: `admin123`)
- Create, edit, and delete parking lots
- Automatic parking spot generation
- View real-time occupancy status
- User management
- Revenue reports and analytics
- Search and filter functionality

### User Features
- User registration and login
- Browse available parking lots
- Book parking spots (auto-assigned)
- Release parking spots with automatic billing
- View parking history
- Personal spending analytics

## Technology Stack

- **Backend**: Python Flask, SQLAlchemy ORM
- **Database**: SQLite (auto-generated)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome

## Installation & Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the application**:
   Open your web browser and go to `http://localhost:5000`

## Project Structure

```
vehicle-parking-app/
├── app.py                  # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── models/                # Database models
│   ├── __init__.py
│   ├── admin.py
│   ├── user.py
│   ├── parking_lot.py
│   ├── parking_spot.py
│   └── reservation.py
├── routes/                # Application routes
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── admin_routes.py
│   └── user_routes.py
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin/            # Admin templates
│   └── user/             # User templates
├── static/               # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── charts.js
├── README.md             # This file
└── project_report.docx   # Detailed project report
```

## Database Models

1. **AdminModel**: Admin authentication and management
2. **UserModel**: User registration and profile management
3. **ParkingLotModel**: Parking facility information
4. **ParkingSpotModel**: Individual parking spot tracking
5. **ReservationModel**: Booking and billing records

## Default Login Credentials

- **Admin**: 
  - Username: `aakash`
  - Password: `24f2003480`

- **Users**: Register new accounts through the registration page

## Features Implemented

### Core Functionality
- ✅ Multi-user authentication system
- ✅ Admin dashboard with full CRUD operations
- ✅ Automatic parking spot generation
- ✅ Real-time occupancy tracking
- ✅ Automatic billing calculation
- ✅ Responsive web design

### Advanced Features
- ✅ Search and filtering capabilities
- ✅ Interactive charts and analytics
- ✅ Form validation (both client and server-side)
- ✅ Auto-refresh for real-time updates
- ✅ Export functionality (placeholders)
- ✅ Mobile-responsive design

## API Endpoints

### Authentication
- `GET/POST /login` - User/Admin login
- `GET/POST /register` - User registration
- `GET /logout` - Logout

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/parking-lots` - View all parking lots
- `GET/POST /admin/parking-lots/add` - Add new parking lot
- `GET/POST /admin/parking-lots/<id>/edit` - Edit parking lot
- `GET /admin/users` - View all users
- `GET /admin/reports` - Reports and analytics

### User Routes
- `GET /user/dashboard` - User dashboard
- `GET /user/book-parking` - Browse parking lots
- `GET/POST /user/book-parking/<lot_id>` - Book specific lot
- `GET /user/release-parking/<reservation_id>` - Release parking spot
- `GET /user/history` - View parking history

## Database Schema

The SQLite database is automatically created with the following tables:
- `admins` - Admin accounts
- `users` - User accounts
- `parking_lots` - Parking facility information
- `parking_spots` - Individual parking spots
- `reservations` - Booking records
