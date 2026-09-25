from flask import Blueprint, jsonify, render_template
from app.routes import login_required, get_current_user
from app.services.analytics_service import get_user_analytics_summary

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/progress', methods=['GET'])
@login_required
def progress_view():
    user = get_current_user()
    return render_template('progress.html', user=user, active_page='progress')


@analytics_bp.route('/api/analytics/summary', methods=['GET'])
@login_required
def api_get_analytics_summary():
    user = get_current_user()
    data = get_user_analytics_summary(user.id)
    if not data:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify(data), 200
