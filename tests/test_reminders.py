from datetime import date, timedelta


def test_reminder_preferences(auth_client):
    res = auth_client.get('/api/reminders/preferences')
    assert res.status_code == 200
    prefs = res.get_json()['preferences']
    assert prefs['daily_fitness_reminder'] is True
    assert prefs['hydration_target'] == 2.0

    # Update preferences
    up_res = auth_client.put('/api/reminders/preferences', json={
        'daily_fitness_reminder': False,
        'hydration_target': 3.0
    })
    assert up_res.status_code == 200
    up_prefs = up_res.get_json()['preferences']
    assert up_prefs['daily_fitness_reminder'] is False
    assert up_prefs['hydration_target'] == 3.0


def test_invalid_hydration_target(auth_client):
    res = auth_client.put('/api/reminders/preferences', json={
        'hydration_target': -1.0
    })
    assert res.status_code == 400


def test_active_reminders_triggering(auth_client):
    # Fresh user: has no workouts or fitness metrics logged today
    res = auth_client.get('/api/reminders/active')
    assert res.status_code == 200
    reminders = res.get_json()['reminders']
    rem_ids = [r['id'] for r in reminders]
    assert 'daily_fitness' in rem_ids
    assert 'daily_workout' in rem_ids

    # Add goal with deadline tomorrow
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    auth_client.post('/api/goals', json={
        'goal_type': 'Weight Loss',
        'target_value': 65.0,
        'current_value': 70.0,
        'deadline': tomorrow
    })

    res2 = auth_client.get('/api/reminders/active')
    rem_ids2 = [r['id'] for r in res2.get_json()['reminders']]
    assert any('goal_due_' in rid for rid in rem_ids2)
