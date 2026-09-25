from datetime import datetime, date, timezone
from app.models import db


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    exercise_name = db.Column(db.String(120), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Float, nullable=False)
    workout_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_name': self.exercise_name,
            'exercise_type': self.exercise_type,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'workout_date': self.workout_date.isoformat() if self.workout_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
