from flask import Blueprint, request, jsonify, render_template
from app.models import Workout
from app.routes import login_required, get_current_user
from app.services.workout_service import (
    create_workout,
    get_workouts,
    get_workout_by_id,
    delete_workout
)

workout_bp = Blueprint('workout', __name__)


@workout_bp.route('/workouts', methods=['GET'])
@login_required
def workouts_view():
    user = get_current_user()
    return render_template('workouts.html', user=user, active_page='workouts')


@workout_bp.route('/api/workouts', methods=['GET'])
@login_required
def api_get_workouts():
    user = get_current_user()
    workouts = get_workouts(user.id)
    return jsonify({
        'success': True,
        'count': len(workouts),
        'workouts': [w.to_dict() for w in workouts]
    }), 200


@workout_bp.route('/api/workouts', methods=['POST'])
@login_required
def api_create_workout():
    user = get_current_user()
    data = request.get_json() or {}

    workout, error = create_workout(user.id, data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'Workout logged successfully',
        'workout': workout.to_dict()
    }), 201


@workout_bp.route('/api/workouts/<int:workout_id>', methods=['GET'])
@login_required
def api_get_workout(workout_id):
    user = get_current_user()
    workout = get_workout_by_id(workout_id, user.id)
    if not workout:
        # Check if workout belongs to another user
        other = Workout.query.filter_by(id=workout_id).first()
        if other:
            return jsonify({'success': False, 'message': 'Unauthorized access to workout record'}), 403
        return jsonify({'success': False, 'message': 'Workout not found'}), 404

    return jsonify({
        'success': True,
        'workout': workout.to_dict()
    }), 200


@workout_bp.route('/api/workouts/<int:workout_id>', methods=['DELETE'])
@login_required
def api_delete_workout(workout_id):
    user = get_current_user()
    success, error = delete_workout(workout_id, user.id)
    if not success:
        status_code = 403 if "Unauthorized" in (error or "") else 404
        return jsonify({'success': False, 'message': error or 'Failed to delete workout'}), status_code

    return jsonify({
        'success': True,
        'message': 'Workout deleted successfully'
    }), 200
