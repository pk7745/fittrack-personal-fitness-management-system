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

        # Seed initial demo account if not testing
        if config_name != 'testing':
            try:
                from app.models import User, Workout, FitnessRecord, Goal, ReminderPreference
                from datetime import date, timedelta
                demo_user = User.query.filter_by(email='demo@fittrack.com').first()
                if not demo_user:
                    demo_user = User(
                        name='Pavan Kumar',
                        email='demo@fittrack.com',
                        age=24,
                        gender='Male',
                        height=175.0,
                        weight=68.5,
                        fitness_goal='Muscle Building & General Fitness'
                    )
                    demo_user.set_password('Password123!')
                    db.session.add(demo_user)
                    db.session.commit()

                    today = date.today()
                    sample_weights = [70.0, 69.8, 69.5, 69.2, 69.0, 68.7, 68.5]
                    sample_waters = [2.0, 2.4, 1.8, 2.5, 2.2, 2.7, 2.5]
                    sample_calories = [2100, 1950, 2200, 1850, 2050, 1900, 1850]
                    for i in range(7):
                        rec = FitnessRecord(
                            user_id=demo_user.id,
                            record_date=today - timedelta(days=6 - i),
                            weight=sample_weights[i],
                            height=175.0,
                            water_intake=sample_waters[i],
                            calories_burned=sample_calories[i]
                        )
                        db.session.add(rec)

                    sample_workouts = [
                        (today - timedelta(days=5), 'Running', 35, 340, 'Morning endurance run'),
                        (today - timedelta(days=4), 'Strength Training', 50, 420, 'Upper body hypertrophy'),
                        (today - timedelta(days=2), 'Cycling', 45, 380, 'Outdoor interval cycling'),
                        (today - timedelta(days=1), 'HIIT', 30, 310, 'Core and cardio circuit'),
                        (today, 'Strength Training', 60, 480, 'Legs and shoulders session')
                    ]
                    for w_date, w_type, w_dur, w_cal, w_notes in sample_workouts:
                        db.session.add(Workout(
                            user_id=demo_user.id,
                            date=w_date,
                            workout_type=w_type,
                            duration=w_dur,
                            calories_burned=w_cal,
                            notes=w_notes
                        ))

                    g1 = Goal(
                        user_id=demo_user.id,
                        goal_type='Weight Loss',
                        target_value=65.0,
                        current_value=68.5,
                        start_value=70.0,
                        deadline=today + timedelta(days=45),
                        status='In Progress'
                    )
                    g2 = Goal(
                        user_id=demo_user.id,
                        goal_type='Muscle Building',
                        target_value=20.0,
                        current_value=12.0,
                        start_value=0.0,
                        deadline=today + timedelta(days=30),
                        status='In Progress'
                    )
                    pref = ReminderPreference(
                        user_id=demo_user.id,
                        workout_reminder=True,
                        daily_fitness_reminder=True,
                        goal_deadline_reminder=True,
                        hydration_reminder=True,
                        hydration_target=2.5
                    )
                    db.session.add_all([g1, g2, pref])
                    db.session.commit()
            except Exception:
                db.session.rollback()

    return app
