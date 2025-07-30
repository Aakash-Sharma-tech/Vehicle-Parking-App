from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, AdminModel, UserModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission"""
    username = request.form.get('username')
    password = request.form.get('password')
    user_type = request.form.get('user_type')
    
    if not username or not password:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.login'))
    
    if user_type == 'admin':
        # Admin login
        admin = AdminModel.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_id'] = admin.id
            session['username'] = admin.username
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    else:
        # User login
        user = UserModel.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = False
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid user credentials or account disabled', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/register')
def register():
    """Registration page"""
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register_post():
    """Handle registration form submission"""
    username = request.form.get('username')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Basic validation
    if not all([username, email, full_name, phone, password, confirm_password]):
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.register'))
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth.register'))
    
    # Check if username or email already exists
    existing_user = UserModel.query.filter(
        (UserModel.username == username) | (UserModel.email == email)
    ).first()
    
    if existing_user:
        flash('Username or email already exists', 'error')
        return redirect(url_for('auth.register'))
    
    # Create new user
    try:
        new_user = UserModel(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('auth.register'))

@auth_bp.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))