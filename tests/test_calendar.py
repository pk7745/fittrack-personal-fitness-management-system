from datetime import date


def test_unauthenticated_calendar_rejection(client):
    assert client.get('/api/calendar/month').status_code == 401


def test_calendar_month_events(auth_client):
    today = date.today()
    # Log workout on today
    auth_client.post('/api/workouts', json={
        'exercise_name': 'Calendar Pilates',
        'exercise_type': 'Other',
        'duration': 35,
        'calories_burned': 160.0,
        'workout_date': today.isoformat()
    })

    res = auth_client.get(f'/api/calendar/month?year={today.year}&month={today.month}')
    assert res.status_code == 200
    cal_data = res.get_json()['calendar']
    assert cal_data['year'] == today.year
    assert cal_data['month'] == today.month
    events = cal_data['events']
    assert today.isoformat() in events
    today_event = events[today.isoformat()]
    assert today_event['has_workout'] is True
    assert today_event['workout_count'] == 1
    assert today_event['workouts'][0]['exercise_name'] == 'Calendar Pilates'


def test_calendar_invalid_month(auth_client):
    res = auth_client.get('/api/calendar/month?year=2026&month=13')
    assert res.status_code == 400


def test_calendar_user_isolation(client):
    today = date.today()
    client.post('/api/auth/register', json={
        'name': 'Cal User 1',
        'email': 'cu1@example.com',
        'password': 'password123'
    })
    client.post('/api/workouts', json={
        'exercise_name': 'User 1 Secret Run',
        'exercise_type': 'Running',
        'duration': 20,
        'calories_burned': 180.0,
        'workout_date': today.isoformat()
    })
    client.post('/api/auth/logout')

    # User 2 logs in
    client.post('/api/auth/register', json={
        'name': 'Cal User 2',
        'email': 'cu2@example.com',
        'password': 'password123'
    })
    res_u2 = client.get(f'/api/calendar/month?year={today.year}&month={today.month}')
    assert res_u2.status_code == 200
    events_u2 = res_u2.get_json()['calendar']['events']
    # User 2 must see 0 workouts on today
    assert events_u2[today.isoformat()]['workout_count'] == 0
