from datetime import date
from flask import Blueprint, request, jsonify, render_template
from app.models import db, User, FitnessRecord
from app.routes import login_required, get_current_user
from app.services.fitness_service import calculate_bmi, get_bmi_category

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET'])
@login_required
def profile_view():
    user = get_current_user()
    return render_template('profile.html', user=user, active_page='profile')


@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    user = get_current_user()
    bmi = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi)

    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'bmi': bmi,
        'bmi_category': bmi_category
    }), 200


@profile_bp.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    user = get_current_user()
    data = request.get_json() or {}

    # Name validation
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Name cannot be empty'}), 400
        if len(name) < 2 or len(name) > 100:
            return jsonify({'success': False, 'message': 'Name must be between 2 and 100 characters'}), 400
        user.name = name

    # Age validation
    if 'age' in data:
        age = data.get('age')
        if age is not None and age != "":
            try:
                age_val = int(age)
                if age_val < 5 or age_val > 120:
                    return jsonify({'success': False, 'message': 'Age must be between 5 and 120'}), 400
                user.age = age_val
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Age must be a valid number'}), 400
        else:
            user.age = None

    # Gender
    if 'gender' in data:
        user.gender = (data.get('gender') or '').strip() or None

    # Height validation (in cm)
    if 'height' in data:
        height = data.get('height')
        if height is not None and height != "":
            try:
                h_val = float(height)
                if h_val < 50 or h_val > 300:
                    return jsonify({'success': False, 'message': 'Height must be between 50 and 300 cm'}), 400
                user.height = h_val
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Height must be a valid number'}), 400
        else:
            user.height = None

    # Weight validation (in kg)
    if 'weight' in data:
        weight = data.get('weight')
        if weight is not None and weight != "":
            try:
                w_val = float(weight)
                if w_val < 20 or w_val > 500:
                    return jsonify({'success': False, 'message': 'Weight must be between 20 and 500 kg'}), 400
                user.weight = w_val
                # Sync today's fitness record weight if one exists
                today_rec = FitnessRecord.query.filter_by(user_id=user.id, record_date=date.today()).first()
                if today_rec:
                    today_rec.weight = w_val
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Weight must be a valid number'}), 400
        else:
            user.weight = None

    # Fitness goal
    if 'fitness_goal' in data:
        user.fitness_goal = (data.get('fitness_goal') or '').strip() or 'General Fitness'

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    bmi = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi)

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': user.to_dict(),
        'bmi': bmi,
        'bmi_category': bmi_category
    }), 200
