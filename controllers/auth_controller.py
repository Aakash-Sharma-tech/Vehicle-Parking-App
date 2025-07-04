from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import User

auth_bp = Blueprint('auth', __name__)

# Admin credentials (hardcoded as requested)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form.get('user_type', 'user')
        
        if user_type == 'admin':
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid admin credentials!', 'danger')
        else:
            user = User.authenticate(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('user.dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Validation
        if not username or not password:
            flash('Username and password are required!', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match!', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
        else:
            if User.create(username, password, email, phone):
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Username already exists!', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('index'))