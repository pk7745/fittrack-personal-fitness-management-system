from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from app.models import db, Goal
from app.routes import login_required, get_current_user
from app.services.fitness_service import calculate_goal_progress

goal_bp = Blueprint('goal', __name__)

VALID_GOAL_TYPES = [
    'Weight Loss',
    'Weight Gain',
    'Muscle Building',
    'General Fitness',
    'Endurance'
]


@goal_bp.route('/goals', methods=['GET'])
@login_required
def goals_view():
    user = get_current_user()
    return render_template('goals.html', user=user, active_page='goals')


@goal_bp.route('/api/goals', methods=['GET'])
@login_required
def api_get_goals():
    user = get_current_user()
    goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.created_at.desc()).all()

    result = []
    for g in goals:
        progress = calculate_goal_progress(
            g.goal_type,
            g.target_value,
            g.current_value,
            start_value=g.start_value,
            deadline=g.deadline
        )
        data = g.to_dict()
        data['progress_percentage'] = progress['percentage']
        data['is_completed'] = progress['is_completed']
        data['status'] = progress['status']
        data['remaining_days'] = progress['remaining_days']
        result.append(data)

    return jsonify({
        'success': True,
        'goals': result
    }), 200


@goal_bp.route('/api/goals/<int:goal_id>', methods=['GET'])
@login_required
def api_get_goal(goal_id):
    user = get_current_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        other = Goal.query.filter_by(id=goal_id).first()
        if other:
            return jsonify({'success': False, 'message': 'Unauthorized access to goal'}), 403
        return jsonify({'success': False, 'message': 'Goal not found'}), 404

    progress = calculate_goal_progress(
        goal.goal_type,
        goal.target_value,
        goal.current_value,
        start_value=goal.start_value,
        deadline=goal.deadline
    )
    resp = goal.to_dict()
    resp['progress_percentage'] = progress['percentage']
    resp['is_completed'] = progress['is_completed']
    resp['status'] = progress['status']
    resp['remaining_days'] = progress['remaining_days']

    return jsonify({
        'success': True,
        'goal': resp
    }), 200


@goal_bp.route('/api/goals', methods=['POST'])
@login_required
def api_create_goal():
    user = get_current_user()
    data = request.get_json() or {}

    goal_type = (data.get('goal_type') or '').strip()
    if not goal_type or goal_type not in VALID_GOAL_TYPES:
        return jsonify({
            'success': False,
            'message': f'Goal type must be one of: {", ".join(VALID_GOAL_TYPES)}'
        }), 400

    target_val = data.get('target_value')
    if target_val is None or target_val == "":
        return jsonify({'success': False, 'message': 'Target value is required'}), 400
    try:
        target_val = float(target_val)
        if target_val <= 0:
            return jsonify({'success': False, 'message': 'Target value must be greater than 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Target value must be a valid number'}), 400

    curr_val = data.get('current_value', 0.0)
    try:
        curr_val = float(curr_val) if curr_val is not None else 0.0
        if curr_val < 0:
            return jsonify({'success': False, 'message': 'Current value cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Current value must be a valid number'}), 400

    # Optional start_value (baseline)
    start_val = data.get('start_value')
    if start_val is not None and start_val != "":
        try:
            start_val = float(start_val)
            if start_val <= 0:
                return jsonify({'success': False, 'message': 'Start value must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Start value must be a valid number'}), 400
    else:
        start_val = None

    # Optional deadline
    deadline_str = data.get('deadline')
    deadline_date = None
    if deadline_str:
        try:
            deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid deadline format. Use YYYY-MM-DD'}), 400

    goal = Goal(
        user_id=user.id,
        goal_type=goal_type,
        target_value=target_val,
        current_value=curr_val,
        start_value=start_val,
        deadline=deadline_date
    )

    try:
        db.session.add(goal)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    progress = calculate_goal_progress(
        goal.goal_type,
        goal.target_value,
        goal.current_value,
        start_value=goal.start_value,
        deadline=goal.deadline
    )
    resp = goal.to_dict()
    resp['progress_percentage'] = progress['percentage']
    resp['is_completed'] = progress['is_completed']
    resp['status'] = progress['status']
    resp['remaining_days'] = progress['remaining_days']

    return jsonify({
        'success': True,
        'message': 'Goal created successfully',
        'goal': resp
    }), 201


@goal_bp.route('/api/goals/<int:goal_id>', methods=['PUT'])
@login_required
def api_update_goal(goal_id):
    user = get_current_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        other = Goal.query.filter_by(id=goal_id).first()
        if other:
            return jsonify({'success': False, 'message': 'Unauthorized access to goal'}), 403
        return jsonify({'success': False, 'message': 'Goal not found'}), 404

    data = request.get_json() or {}

    if 'goal_type' in data:
        gtype = (data.get('goal_type') or '').strip()
        if gtype in VALID_GOAL_TYPES:
            goal.goal_type = gtype

    if 'target_value' in data:
        try:
            t_val = float(data.get('target_value'))
            if t_val <= 0:
                return jsonify({'success': False, 'message': 'Target value must be greater than 0'}), 400
            goal.target_value = t_val
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Target value must be a valid number'}), 400

    if 'current_value' in data:
        try:
            c_val = float(data.get('current_value'))
            if c_val < 0:
                return jsonify({'success': False, 'message': 'Current value cannot be negative'}), 400
            goal.current_value = c_val
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Current value must be a valid number'}), 400

    if 'start_value' in data:
        s_val = data.get('start_value')
        if s_val is not None and s_val != "":
            try:
                s_num = float(s_val)
                if s_num <= 0:
                    return jsonify({'success': False, 'message': 'Start value must be greater than 0'}), 400
                goal.start_value = s_num
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Start value must be a valid number'}), 400
        else:
            goal.start_value = None

    if 'deadline' in data:
        d_val = data.get('deadline')
        if d_val:
            try:
                goal.deadline = datetime.strptime(d_val, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid deadline format. Use YYYY-MM-DD'}), 400
        else:
            goal.deadline = None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    progress = calculate_goal_progress(
        goal.goal_type,
        goal.target_value,
        goal.current_value,
        start_value=goal.start_value,
        deadline=goal.deadline
    )
    resp = goal.to_dict()
    resp['progress_percentage'] = progress['percentage']
    resp['is_completed'] = progress['is_completed']
    resp['status'] = progress['status']
    resp['remaining_days'] = progress['remaining_days']

    return jsonify({
        'success': True,
        'message': 'Goal updated successfully',
        'goal': resp
    }), 200


@goal_bp.route('/api/goals/<int:goal_id>', methods=['DELETE'])
@login_required
def api_delete_goal(goal_id):
    user = get_current_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        other = Goal.query.filter_by(id=goal_id).first()
        if other:
            return jsonify({'success': False, 'message': 'Unauthorized access to goal'}), 403
        return jsonify({'success': False, 'message': 'Goal not found'}), 404

    try:
        db.session.delete(goal)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': 'Goal deleted successfully'
    }), 200
