from datetime import datetime, timezone
from app.models import db


class ReminderPreference(db.Model):
    __tablename__ = 'reminder_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    workout_reminder = db.Column(db.Boolean, default=True, nullable=False)
    daily_fitness_reminder = db.Column(db.Boolean, default=True, nullable=False)
    goal_deadline_reminder = db.Column(db.Boolean, default=True, nullable=False)
    hydration_reminder = db.Column(db.Boolean, default=True, nullable=False)
    hydration_target = db.Column(db.Float, default=2.0, nullable=False)  # in Litres
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workout_reminder': self.workout_reminder,
            'daily_fitness_reminder': self.daily_fitness_reminder,
            'goal_deadline_reminder': self.goal_deadline_reminder,
            'hydration_reminder': self.hydration_reminder,
            'hydration_target': self.hydration_target,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
