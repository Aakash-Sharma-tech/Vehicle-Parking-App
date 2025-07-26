from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from models.admin_model import AdminModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if admin
        admin = AdminModel.authenticate_admin(email, password)
        if admin:
            session['user'] = admin
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        # Check regular user
        user = UserModel.authenticate_user(email, password)
        if user:
            session['user'] = user
            session['is_admin'] = False
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        
        flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if UserModel.email_exists(email):
            flash('Email already exists!', 'error')
            return render_template('register.html')
        
        if UserModel.create_user(name, email, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        
        flash('Registration failed!', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))