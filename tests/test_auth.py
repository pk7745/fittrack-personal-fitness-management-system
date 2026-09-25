def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'name': 'Alex Morgan',
        'email': 'alex@example.com',
        'password': 'SecurePass123',
        'height': 170.0,
        'weight': 65.0
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['email'] == 'alex@example.com'
    assert data['user']['name'] == 'Alex Morgan'


def test_register_duplicate_email(client):
    payload = {
        'name': 'User One',
        'email': 'duplicate@example.com',
        'password': 'password123'
    }
    res1 = client.post('/api/auth/register', json=payload)
    assert res1.status_code == 201

    res2 = client.post('/api/auth/register', json=payload)
    assert res2.status_code == 409
    assert res2.get_json()['success'] is False


def test_register_validation(client):
    # Short password
    res = client.post('/api/auth/register', json={
        'name': 'Bob',
        'email': 'bob@example.com',
        'password': '123'
    })
    assert res.status_code == 400

    # Invalid email
    res = client.post('/api/auth/register', json={
        'name': 'Bob',
        'email': 'not-an-email',
        'password': 'password123'
    })
    assert res.status_code == 400


def test_login_success(client):
    client.post('/api/auth/register', json={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    })

    res = client.post('/api/auth/login', json={
        'email': 'john@example.com',
        'password': 'password123'
    })
    assert res.status_code == 200
    assert res.get_json()['success'] is True


def test_login_invalid_password(client):
    client.post('/api/auth/register', json={
        'name': 'John Doe',
        'email': 'john2@example.com',
        'password': 'password123'
    })

    res = client.post('/api/auth/login', json={
        'email': 'john2@example.com',
        'password': 'wrongpassword'
    })
    assert res.status_code == 401
    assert res.get_json()['success'] is False


def test_logout(auth_client):
    res = auth_client.post('/api/auth/logout')
    assert res.status_code == 200

    # Next call should be unauthorized
    res_me = auth_client.get('/api/auth/me')
    assert res_me.status_code == 401


def test_unauthorized_access(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401
    assert res.get_json()['success'] is False
