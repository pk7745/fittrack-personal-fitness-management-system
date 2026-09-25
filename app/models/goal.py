from datetime import datetime, timezone
from app.models import db


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    goal_type = db.Column(db.String(50), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False, default=0.0)
    start_value = db.Column(db.Float, nullable=True)  # v1.1: Baseline value
    deadline = db.Column(db.Date, nullable=True)      # v1.1: Goal target date
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'start_value': self.start_value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
