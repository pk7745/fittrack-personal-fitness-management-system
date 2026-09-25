from flask import Blueprint, request, jsonify
from app.models import db, FitnessRecord
from app.routes import login_required, get_current_user
from app.services.fitness_service import (
    save_fitness_record,
    get_user_fitness_history,
    get_daily_fitness_summary
)

fitness_bp = Blueprint('fitness', __name__)


@fitness_bp.route('/api/fitness', methods=['GET'])
@login_required
def api_get_fitness():
    user = get_current_user()
    limit = request.args.get('limit', default=30, type=int)
    history = get_user_fitness_history(user.id, limit=limit)
    summary = get_daily_fitness_summary(user.id)

    return jsonify({
        'success': True,
        'summary': summary,
        'history': history
    }), 200


@fitness_bp.route('/api/fitness', methods=['POST'])
@login_required
def api_save_fitness():
    user = get_current_user()
    data = request.get_json() or {}

    record, error = save_fitness_record(user.id, data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    # Get updated summary for immediate UI refresh
    summary = get_daily_fitness_summary(user.id, record.record_date)

    return jsonify({
        'success': True,
        'message': 'Fitness metrics saved successfully',
        'record': record.to_dict(),
        'summary': summary
    }), 201


@fitness_bp.route('/api/fitness/<int:record_id>', methods=['DELETE'])
@login_required
def api_delete_fitness(record_id):
    user = get_current_user()
    record = FitnessRecord.query.filter_by(id=record_id, user_id=user.id).first()
    if not record:
        other = FitnessRecord.query.filter_by(id=record_id).first()
        if other:
            return jsonify({'success': False, 'message': 'Unauthorized access to fitness record'}), 403
        return jsonify({'success': False, 'message': 'Fitness record not found'}), 404

    try:
        db.session.delete(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': 'Fitness record deleted successfully'
    }), 200
