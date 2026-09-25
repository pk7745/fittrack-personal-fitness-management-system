import os
from flask import Flask, jsonify, render_template, request
from sqlalchemy import event
from sqlalchemy.engine import Engine
from config import config
from app.models import db


# Enforce SQLite foreign key constraints and cascading behavior
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_name='default'):
    """Application factory for FitTrack."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    cfg = config.get(config_name, config['default'])
    app.config.from_object(cfg)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.workout import workout_bp
    from app.routes.fitness import fitness_bp
    from app.routes.profile import profile_bp
    from app.routes.goal import goal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(fitness_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(goal_bp)

    # Global Error Handlers (returning JSON for API, HTML for web)
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Bad request'}), 400
        return render_template('base.html', error_title="400 - Bad Request", error_msg="The request could not be understood."), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return render_template('base.html', error_title="401 - Unauthorized", error_msg="Please log in to continue."), 401

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Forbidden. You do not have permission.'}), 403
        return render_template('base.html', error_title="403 - Forbidden", error_msg="Access denied."), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Resource not found'}), 404
        return render_template('base.html', error_title="404 - Not Found", error_msg="The requested page could not be found."), 404

    @app.errorhandler(409)
    def conflict(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Conflict occurred.'}), 409
        return render_template('base.html', error_title="409 - Conflict", error_msg="Resource conflict."), 409

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
        return render_template('base.html', error_title="500 - Server Error", error_msg="An unexpected error occurred."), 500

    # Initialize database tables
    with app.app_context():
        db.create_all()

    return app
