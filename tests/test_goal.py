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
