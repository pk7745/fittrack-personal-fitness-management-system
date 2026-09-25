def test_unauthenticated_reports_rejection(client):
    assert client.get('/api/reports/fitness.csv').status_code == 401
    assert client.get('/api/reports/workouts.csv').status_code == 401
    assert client.get('/api/reports/goals.csv').status_code == 401
    assert client.get('/api/reports/summary.csv').status_code == 401
    assert client.get('/api/reports/fitness.pdf').status_code == 401


def test_csv_export_structure(auth_client):
    # Log sample workout and fitness metric
    auth_client.post('/api/workouts', json={
        'exercise_name': 'Report Test Exercise',
        'exercise_type': 'Strength',
        'duration': 45,
        'calories_burned': 320.0
    })
    auth_client.post('/api/fitness', json={
        'weight': 68.0,
        'water_intake': 2.5,
        'calories_consumed': 2100
    })

    # Workouts CSV
    res_w = auth_client.get('/api/reports/workouts.csv')
    assert res_w.status_code == 200
    assert res_w.headers['Content-Type'].startswith('text/csv')
    assert 'Report Test Exercise' in res_w.data.decode('utf-8')
    assert 'Exercise Name' in res_w.data.decode('utf-8')

    # Fitness CSV
    res_f = auth_client.get('/api/reports/fitness.csv')
    assert res_f.status_code == 200
    assert '68.0' in res_f.data.decode('utf-8')

    # Summary CSV
    res_s = auth_client.get('/api/reports/summary.csv')
    assert res_s.status_code == 200
    assert 'Metric,Value' in res_s.data.decode('utf-8')


def test_pdf_export(auth_client):
    res_pdf = auth_client.get('/api/reports/fitness.pdf')
    assert res_pdf.status_code == 200
    assert res_pdf.headers['Content-Type'] == 'application/pdf'
    assert res_pdf.data.startswith(b'%PDF')


def test_report_user_isolation(client):
    # User 1 registers and logs workout
    client.post('/api/auth/register', json={
        'name': 'Report User 1',
        'email': 'ru1@example.com',
        'password': 'password123'
    })
    client.post('/api/workouts', json={
        'exercise_name': 'User 1 Confidential Workout',
        'exercise_type': 'Cardio',
        'duration': 50,
        'calories_burned': 400.0
    })
    client.post('/api/auth/logout')

    # User 2 logs in
    client.post('/api/auth/register', json={
        'name': 'Report User 2',
        'email': 'ru2@example.com',
        'password': 'password123'
    })

    # User 2 downloads workouts CSV -> must NOT contain User 1's workout
    res_u2 = client.get('/api/reports/workouts.csv')
    assert res_u2.status_code == 200
    content = res_u2.data.decode('utf-8')
    assert 'User 1 Confidential Workout' not in content
