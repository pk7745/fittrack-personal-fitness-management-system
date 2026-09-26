import os
import sys
from datetime import date, timedelta
from app import create_app
from app.models import db, User, Workout, FitnessRecord, Goal, ReminderPreference

# Determine environment: honor FLASK_CONFIG, FLASK_ENV, or auto-detect Render
env_name = os.environ.get('FLASK_CONFIG') or os.environ.get('FLASK_ENV')
if not env_name:
    env_name = 'production' if os.environ.get('RENDER') else 'development'

app = create_app(env_name)


def seed_demo_data():
    """Seed sample data for demonstration / college presentation."""
    with app.app_context():
        # Check if demo user already exists
        demo_user = User.query.filter_by(email='demo@fittrack.com').first()
        if demo_user:
            print("Demo user already exists. Cleaning up old demo records...")
            db.session.delete(demo_user)
            db.session.commit()

        print("Creating demo user: demo@fittrack.com / Password123!")
        demo_user = User(
            name='Pavan Kumar',
            email='demo@fittrack.com',
            age=24,
            gender='Male',
            height=175.0,  # 175 cm
            weight=68.5,   # 68.5 kg -> BMI ~ 22.4
            fitness_goal='Muscle Building & General Fitness'
        )
        demo_user.set_password('Password123!')
        db.session.add(demo_user)
        db.session.commit()

        # Add 7 days of fitness records
        today = date.today()
        sample_weights = [70.0, 69.8, 69.5, 69.2, 69.0, 68.7, 68.5]
        sample_waters = [2.0, 2.4, 1.8, 2.5, 2.2, 2.7, 2.5]
        sample_calories = [2100, 1950, 2200, 1850, 2050, 1900, 1850]

        for i in range(7):
            day = today - timedelta(days=6 - i)
            rec = FitnessRecord(
                user_id=demo_user.id,
                weight=sample_weights[i],
                water_intake=sample_waters[i],
                calories_consumed=sample_calories[i],
                record_date=day
            )
            db.session.add(rec)

        # Add sample workouts across the week
        workouts_data = [
            ("Morning Jog", "Running", 30, 280.0, today - timedelta(days=6)),
            ("Upper Body Hypertrophy", "Strength", 45, 340.0, today - timedelta(days=5)),
            ("Vinyasa Yoga Flow", "Yoga", 40, 160.0, today - timedelta(days=4)),
            ("HIIT Cardio Blast", "Cardio", 25, 290.0, today - timedelta(days=3)),
            ("Leg Day & Squats", "Strength", 50, 410.0, today - timedelta(days=2)),
            ("Evening Cycle Ride", "Cycling", 35, 260.0, today - timedelta(days=1)),
            ("Core & Push Workout", "Strength", 40, 310.0, today),
            ("Brisk Walk", "Walking", 20, 110.0, today)
        ]

        for name, ex_type, duration, cals, w_date in workouts_data:
            w = Workout(
                user_id=demo_user.id,
                exercise_name=name,
                exercise_type=ex_type,
                duration=duration,
                calories_burned=cals,
                workout_date=w_date
            )
            db.session.add(w)

        # Add sample goals with v1.1 start_value and deadline
        goals_data = [
            ("Weight Loss", 65.0, 68.5, 72.0, today + timedelta(days=14)),
            ("Muscle Building", 500.0, 350.0, 100.0, today + timedelta(days=30)),
            ("Endurance", 30.0, 18.0, 0.0, today + timedelta(days=2))
        ]
        for g_type, target, current, start_val, dline in goals_data:
            g = Goal(
                user_id=demo_user.id,
                goal_type=g_type,
                target_value=target,
                current_value=current,
                start_value=start_val,
                deadline=dline
            )
            db.session.add(g)

        # Add default reminder preferences
        pref = ReminderPreference(
            user_id=demo_user.id,
            workout_reminder=True,
            daily_fitness_reminder=True,
            goal_deadline_reminder=True,
            hydration_reminder=True,
            hydration_target=2.5
        )
        db.session.add(pref)

        db.session.commit()
        print("Demo data seeded successfully for FitTrack v1.1!")
        print("Credentials -> Email: demo@fittrack.com | Password: Password123!")


def ensure_demo_user():
    """Ensure demo user exists on startup so credentials work immediately."""
    with app.app_context():
        try:
            demo_user = User.query.filter_by(email='demo@fittrack.com').first()
            if not demo_user:
                print("Seeding initial demo user for deployment...")
                seed_demo_data()
        except Exception as e:
            print(f"Notice: Auto-seed skipped ({e})")


# Automatically ensure demo user exists
ensure_demo_user()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'seed-demo':
        seed_demo_data()
    else:
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0' if os.environ.get('RENDER') else '127.0.0.1')
        debug = (env_name == 'development')
        print(f"Starting FitTrack v1.1 on http://{host}:{port} (debug={debug}) ...")
        app.run(host=host, port=port, debug=debug)
