from datetime import date, timedelta


def test_unauthenticated_analytics_rejection(client):
    res = client.get('/api/analytics/summary')
    assert res.status_code == 401


def test_empty_analytics(auth_client):
    res = auth_client.get('/api/analytics/summary')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    # Insufficient data states
    assert data['weight_analytics']['trend_7d'] == "Not enough data yet"
    assert data['weight_analytics']['trend_30d'] == "Not enough data yet"
    assert data['workout_analytics']['total_workouts'] == 0
    assert data['workout_analytics']['activity_rate_30d'] == 0.0
    assert data['fitness_analytics']['average_water_intake'] == 0.0


def test_analytics_aggregation_and_trends(auth_client):
    today = date.today()
    # Log 2 weights across 7 days
    auth_client.post('/api/fitness', json={
        'weight': 70.0,
        'water_intake': 2.0,
        'calories_consumed': 2000,
        'record_date': (today - timedelta(days=5)).isoformat()
    })
    auth_client.post('/api/fitness', json={
        'weight': 69.2,
        'water_intake': 2.5,
        'calories_consumed': 1900,
        'record_date': today.isoformat()
    })

    # Log 2 workouts
    auth_client.post('/api/workouts', json={
        'exercise_name': 'Morning Jog',
        'exercise_type': 'Running',
        'duration': 30,
        'calories_burned': 250.0,
        'workout_date': (today - timedelta(days=2)).isoformat()
    })
    auth_client.post('/api/workouts', json={
        'exercise_name': 'Core Session',
        'exercise_type': 'Strength',
        'duration': 40,
        'calories_burned': 300.0,
        'workout_date': today.isoformat()
    })

    res = auth_client.get('/api/analytics/summary')
    assert res.status_code == 200
    data = res.get_json()

    # Weight
    w = data['weight_analytics']
    assert w['starting_weight'] == 70.0
    assert w['current_weight'] == 69.2
    assert w['total_change'] == -0.8
    assert w['trend_7d'] == "-0.8 kg"

    # Workouts
    wo = data['workout_analytics']
    assert wo['total_workouts'] == 2
    assert wo['total_duration_minutes'] == 70
    assert wo['active_days_last_30'] == 2
    assert wo['activity_rate_30d'] == round((2 / 30.0) * 100, 1)

    # Fitness
    f = data['fitness_analytics']
    assert f['average_water_intake'] == 2.25
    assert f['average_calories_consumed'] == 1950
    assert f['average_calories_burned'] == 275.0


def test_analytics_user_isolation(client):
    today = date.today()
    # User 1 registers and logs a workout
    client.post('/api/auth/register', json={
        'name': 'Analytics User 1',
        'email': 'au1@example.com',
        'password': 'password123'
    })
    client.post('/api/workouts', json={
        'exercise_name': 'Private Yoga',
        'exercise_type': 'Yoga',
        'duration': 60,
        'calories_burned': 180.0,
        'workout_date': today.isoformat()
    })
    client.post('/api/auth/logout')

    # User 2 logs in
    client.post('/api/auth/register', json={
        'name': 'Analytics User 2',
        'email': 'au2@example.com',
        'password': 'password123'
    })
    res_u2 = client.get('/api/analytics/summary')
    assert res_u2.status_code == 200
    data_u2 = res_u2.get_json()
    # User 2 must NOT see User 1's workout
    assert data_u2['workout_analytics']['total_workouts'] == 0
    assert data_u2['workout_analytics']['total_duration_minutes'] == 0
