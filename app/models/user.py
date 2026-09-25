from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    height = db.Column(db.Float, nullable=True)  # in cm
    weight = db.Column(db.Float, nullable=True)  # in kg
    fitness_goal = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    workouts = db.relationship('Workout', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    fitness_records = db.relationship('FitnessRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reminder_preference = db.relationship('ReminderPreference', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'fitness_goal': self.fitness_goal,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
