import re
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.models import db, User
from app.routes import login_required, get_current_user

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


# -------------------------------------------------------------
# HTML Views
# -------------------------------------------------------------
@auth_bp.route('/login', methods=['GET'])
def login_view():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET'])
def register_view():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    return render_template('register.html')


@auth_bp.route('/logout', methods=['GET'])
def logout_view():
    session.clear()
    return redirect(url_for('auth.login_view'))


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    # Validations
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'}), 400
    if len(name) < 2 or len(name) > 100:
        return jsonify({'success': False, 'message': 'Name must be between 2 and 100 characters'}), 400

    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({'success': False, 'message': 'Please provide a valid email address'}), 400

    if not password:
        return jsonify({'success': False, 'message': 'Password is required'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Check for existing email (409 Conflict)
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'An account with this email already exists'}), 409

    # Optional fields validation
    age = data.get('age')
    if age is not None and age != "":
        try:
            age = int(age)
            if age < 5 or age > 120:
                return jsonify({'success': False, 'message': 'Age must be between 5 and 120'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Age must be a valid integer'}), 400
    else:
        age = None

    gender = (data.get('gender') or '').strip() or None

    height = data.get('height')
    if height is not None and height != "":
        try:
            height = float(height)
            if height < 50 or height > 300:
                return jsonify({'success': False, 'message': 'Height must be between 50 and 300 cm'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Height must be a valid number'}), 400
    else:
        height = None

    weight = data.get('weight')
    if weight is not None and weight != "":
        try:
            weight = float(weight)
            if weight < 20 or weight > 500:
                return jsonify({'success': False, 'message': 'Weight must be between 20 and 500 kg'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Weight must be a valid number'}), 400
    else:
        weight = None

    fitness_goal = (data.get('fitness_goal') or '').strip() or 'General Fitness'

    # Create user
    user = User(
        name=name,
        email=email,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        fitness_goal=fitness_goal
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error creating user: {str(e)}'}), 500

    # Establish session
    session['user_id'] = user.id
    session.permanent = True

    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    session['user_id'] = user.id
    session.permanent = True

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    user = get_current_user()
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200
