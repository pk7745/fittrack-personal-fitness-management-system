import pytest
from app import create_app
from app.models import db, User


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Register and log in a standard test user."""
    user_data = {
        'name': 'Test User',
        'email': 'tester@example.com',
        'password': 'Password123!',
        'age': 25,
        'gender': 'Female',
        'height': 165.0,
        'weight': 60.0,
        'fitness_goal': 'General Fitness'
    }
    client.post('/api/auth/register', json=user_data)
    return client
