from flask import Blueprint, request, jsonify
from app.routes import login_required, get_current_user
from app.services.calendar_service import get_month_calendar_events

calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.route('/api/calendar/month', methods=['GET'])
@login_required
def api_get_month_calendar():
    user = get_current_user()
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    events_data, error = get_month_calendar_events(user.id, year, month)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'calendar': events_data
    }), 200
