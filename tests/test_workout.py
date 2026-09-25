def test_create_and_get_workout(auth_client):
    res = auth_client.post('/api/workouts', json={
        'exercise_name': 'Bench Press',
        'exercise_type': 'Strength',
        'duration': 45,
        'calories_burned': 320.0,
        'workout_date': '2026-09-25'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['workout']['exercise_name'] == 'Bench Press'

    # Get workouts
    res_list = auth_client.get('/api/workouts')
    assert res_list.status_code == 200
    list_data = res_list.get_json()
    assert list_data['count'] >= 1
    assert any(w['exercise_name'] == 'Bench Press' for w in list_data['workouts'])


def test_create_workout_validation(auth_client):
    # Empty exercise name
    res = auth_client.post('/api/workouts', json={
        'exercise_name': '',
        'exercise_type': 'Cardio',
        'duration': 30,
        'calories_burned': 200
    })
    assert res.status_code == 400

    # Invalid exercise type
    res = auth_client.post('/api/workouts', json={
        'exercise_name': 'Running',
        'exercise_type': 'Skydiving',
        'duration': 30,
        'calories_burned': 200
    })
    assert res.status_code == 400

    # Zero duration
    res = auth_client.post('/api/workouts', json={
        'exercise_name': 'Jogging',
        'exercise_type': 'Running',
        'duration': 0,
        'calories_burned': 200
    })
    assert res.status_code == 400


def test_delete_workout(auth_client):
    res = auth_client.post('/api/workouts', json={
        'exercise_name': 'Swimming',
        'exercise_type': 'Cardio',
        'duration': 30,
        'calories_burned': 250.0
    })
    workout_id = res.get_json()['workout']['id']

    del_res = auth_client.delete(f'/api/workouts/{workout_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True

    get_res = auth_client.get(f'/api/workouts/{workout_id}')
    assert get_res.status_code == 404


def test_unauthorized_workout_access(app, client):
    # User 1 registers and creates a workout
    client.post('/api/auth/register', json={
        'name': 'User One',
        'email': 'u1@example.com',
        'password': 'password123'
    })
    res_w = client.post('/api/workouts', json={
        'exercise_name': 'Secret User 1 Workout',
        'exercise_type': 'Strength',
        'duration': 20,
        'calories_burned': 100
    })
    w_id = res_w.get_json()['workout']['id']
    client.post('/api/auth/logout')

    # User 2 logs in
    client.post('/api/auth/register', json={
        'name': 'User Two',
        'email': 'u2@example.com',
        'password': 'password123'
    })

    # User 2 attempts to read User 1's workout -> must return 403 Forbidden
    get_res = client.get(f'/api/workouts/{w_id}')
    assert get_res.status_code == 403
    assert get_res.get_json()['success'] is False

    # User 2 attempts to delete User 1's workout -> must return 403 Forbidden
    del_res = client.delete(f'/api/workouts/{w_id}')
    assert del_res.status_code == 403
    assert del_res.get_json()['success'] is False

def test_user_cascade_deletion(app, client):
    from app.models import db, User, Workout, FitnessRecord, Goal

    # Register user
    res = client.post('/api/auth/register', json={
        'name': 'Cascade User',
        'email': 'cascade@example.com',
        'password': 'password123'
    })
    user_id = res.get_json()['user']['id']

    # Add workout
    client.post('/api/workouts', json={
        'exercise_name': 'Cascade Workout',
        'exercise_type': 'Cardio',
        'duration': 20,
        'calories_burned': 150
    })

    # Add fitness record
    client.post('/api/fitness', json={
        'weight': 70.0,
        'water_intake': 2.0,
        'calories_consumed': 2000
    })

    # Add goal
    client.post('/api/goals', json={
        'goal_type': 'General Fitness',
        'target_value': 10.0,
        'current_value': 2.0
    })

    with app.app_context():
        user = db.session.get(User, user_id)
        assert user.workouts.count() == 1
        assert user.fitness_records.count() == 1
        assert user.goals.count() == 1

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Verify child records cascade deleted
        assert Workout.query.filter_by(user_id=user_id).count() == 0
        assert FitnessRecord.query.filter_by(user_id=user_id).count() == 0
        assert Goal.query.filter_by(user_id=user_id).count() == 0
