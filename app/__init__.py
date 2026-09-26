import os
from flask import Flask, jsonify, render_template, request
from sqlalchemy import event, text
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
    from app.routes.analytics import analytics_bp
    from app.routes.reminder import reminder_bp
    from app.routes.report import report_bp
    from app.routes.calendar import calendar_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(fitness_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(calendar_bp)

    # Favicon Route
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    # Global Error Handlers (returning JSON for API, HTML for web)
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Bad request'}), 400
        return render_template('404.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return render_template('404.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Forbidden. You do not have permission.'}), 403
        return render_template('404.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Resource not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(409)
    def conflict(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Conflict occurred.'}), 409
        return render_template('404.html'), 409

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
        return render_template('500.html'), 500

    # Initialize database tables and run safe incremental migrations
    with app.app_context():
        # Ensure SQLite target directory exists if using SQLite file
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:///:memory:'):
            file_path = db_uri.replace('sqlite:///', '')
            dir_path = os.path.dirname(file_path)
            if dir_path:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except OSError:
                    pass

        db.create_all()

        # Safe schema migration for SQLite (v1.0 -> v1.1)
        try:
            with db.engine.connect() as conn:
                res = conn.execute(text("PRAGMA table_info(goals);"))
                columns = [row[1] for row in res.fetchall()]
                if 'start_value' not in columns:
                    conn.execute(text("ALTER TABLE goals ADD COLUMN start_value FLOAT;"))
                    conn.commit()
                if 'deadline' not in columns:
                    conn.execute(text("ALTER TABLE goals ADD COLUMN deadline DATE;"))
                    conn.commit()
        except Exception:
            pass

    return app
