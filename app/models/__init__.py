from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import User
from app.models.workout import Workout
from app.models.fitness_record import FitnessRecord
from app.models.goal import Goal

__all__ = ['db', 'User', 'Workout', 'FitnessRecord', 'Goal']
