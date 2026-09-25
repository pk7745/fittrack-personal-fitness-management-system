from flask import Blueprint, request, jsonify
from app.routes import login_required, get_current_user
from app.services.reminders_service import (
    get_or_create_reminder_preferences,
    update_reminder_preferences,
    get_active_reminders
)

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/api/reminders/preferences', methods=['GET'])
@login_required
def api_get_preferences():
    user = get_current_user()
    pref = get_or_create_reminder_preferences(user.id)
    return jsonify({
        'success': True,
        'preferences': pref.to_dict()
    }), 200


@reminder_bp.route('/api/reminders/preferences', methods=['PUT'])
@login_required
def api_update_preferences():
    user = get_current_user()
    data = request.get_json() or {}

    pref, error = update_reminder_preferences(user.id, data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'Reminder preferences updated successfully',
        'preferences': pref.to_dict()
    }), 200


@reminder_bp.route('/api/reminders/active', methods=['GET'])
@login_required
def api_get_active_reminders():
    user = get_current_user()
    reminders = get_active_reminders(user.id)
    return jsonify({
        'success': True,
        'count': len(reminders),
        'reminders': reminders
    }), 200
