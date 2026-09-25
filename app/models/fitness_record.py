from datetime import datetime, date, timezone
from app.models import db


class FitnessRecord(db.Model):
    __tablename__ = 'fitness_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    weight = db.Column(db.Float, nullable=True)
    water_intake = db.Column(db.Float, nullable=True)
    calories_consumed = db.Column(db.Integer, nullable=True)
    record_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weight': self.weight,
            'water_intake': self.water_intake,
            'calories_consumed': self.calories_consumed,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
