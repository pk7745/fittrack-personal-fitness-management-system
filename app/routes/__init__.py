from functools import wraps
from flask import session, jsonify, redirect, url_for, request
from app.models import db, User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            # Check if this is an API call or HTML request
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            return redirect(url_for('auth.login_view'))

        # Verify user still exists in database
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'User session invalid'}), 401
            return redirect(url_for('auth.login_view'))

        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Retrieve currently authenticated user or None."""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None
