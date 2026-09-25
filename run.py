import os
import sys
from datetime import date, timedelta
from app import create_app
from app.models import db, User, Workout, FitnessRecord, Goal

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))


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

        # Add sample goals
        goals_data = [
            ("Weight Loss", 65.0, 68.5),
            ("Strength", 500.0, 350.0),
            ("Endurance", 30.0, 18.0)
        ]
        for g_type, target, current in goals_data:
            g = Goal(
                user_id=demo_user.id,
                goal_type=g_type,
                target_value=target,
                current_value=current
            )
            db.session.add(g)

        db.session.commit()
        print("Demo data seeded successfully!")
        print("Credentials -> Email: demo@fittrack.com | Password: Password123!")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'seed-demo':
        seed_demo_data()
    else:
        print("Starting FitTrack on http://127.0.0.1:5000 ...")
        app.run(host='127.0.0.1', port=5000, debug=True)
