def test_create_and_list_goals(auth_client):
    res = auth_client.post('/api/goals', json={
        'goal_type': 'Weight Loss',
        'target_value': 58.0,
        'current_value': 60.0
    })
    assert res.status_code == 201
    goal = res.get_json()['goal']
    assert goal['goal_type'] == 'Weight Loss'
    assert goal['target_value'] == 58.0

    res_list = auth_client.get('/api/goals')
    assert res_list.status_code == 200
    goals = res_list.get_json()['goals']
    assert len(goals) >= 1


def test_update_and_delete_goal(auth_client):
    res = auth_client.post('/api/goals', json={
        'goal_type': 'Muscle Building',
        'target_value': 100.0,
        'current_value': 20.0
    })
    goal_id = res.get_json()['goal']['id']

    # Update
    up_res = auth_client.put(f'/api/goals/{goal_id}', json={
        'current_value': 50.0
    })
    assert up_res.status_code == 200
    assert up_res.get_json()['goal']['progress_percentage'] == 50.0

    # Delete
    del_res = auth_client.delete(f'/api/goals/{goal_id}')
    assert del_res.status_code == 200


def test_unauthorized_goal_access(client):
    # User 1 registers and creates a goal
    client.post('/api/auth/register', json={
        'name': 'Goal User 1',
        'email': 'gu1@example.com',
        'password': 'password123'
    })
    res_g = client.post('/api/goals', json={
        'goal_type': 'Endurance',
        'target_value': 25.0,
        'current_value': 5.0
    })
    g_id = res_g.get_json()['goal']['id']
    client.post('/api/auth/logout')

    # User 2 logs in
    client.post('/api/auth/register', json={
        'name': 'Goal User 2',
        'email': 'gu2@example.com',
        'password': 'password123'
    })

    # User 2 attempts to get User 1's goal -> 403
    assert client.get(f'/api/goals/{g_id}').status_code == 403

    # User 2 attempts to update User 1's goal -> 403
    assert client.put(f'/api/goals/{g_id}', json={'current_value': 10.0}).status_code == 403

    # User 2 attempts to delete User 1's goal -> 403
    assert client.delete(f'/api/goals/{g_id}').status_code == 403

def test_goal_with_start_value_and_deadline(auth_client):
    from datetime import date, timedelta
    today = date.today()
    deadline_date = (today + timedelta(days=10)).isoformat()

    # Weight Loss: Start = 80 kg, Target = 70 kg, Current = 75 kg
    # Progress: (80 - 75) / (80 - 70) * 100 = 50.0%
    res = auth_client.post('/api/goals', json={
        'goal_type': 'Weight Loss',
        'start_value': 80.0,
        'target_value': 70.0,
        'current_value': 75.0,
        'deadline': deadline_date
    })
    assert res.status_code == 201
    goal = res.get_json()['goal']
    assert goal['start_value'] == 80.0
    assert goal['progress_percentage'] == 50.0
    assert goal['status'] == 'Active'
    assert goal['remaining_days'] == 10

    # Test Overdue status with past deadline
    past_deadline = (today - timedelta(days=5)).isoformat()
    res2 = auth_client.post('/api/goals', json={
        'goal_type': 'General Fitness',
        'target_value': 100.0,
        'current_value': 20.0,
        'deadline': past_deadline
    })
    assert res2.status_code == 201
    goal2 = res2.get_json()['goal']
    assert goal2['status'] == 'Overdue'
    assert goal2['remaining_days'] == -5
