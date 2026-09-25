def test_unauthenticated_page_access(client):
    """Unauthenticated users accessing protected pages should be redirected to /login."""
    protected_pages = [
        '/',
        '/dashboard',
        '/workouts',
        '/progress',
        '/goals',
        '/calendar',
        '/reports',
        '/profile'
    ]
    for page in protected_pages:
        res = client.get(page)
        assert res.status_code == 302
        assert '/login' in res.headers.get('Location', '')


def test_public_pages_access(client):
    """Login and register pages should be publicly accessible without authentication."""
    res_login = client.get('/login')
    assert res_login.status_code == 200
    assert b'Sign In' in res_login.data
    assert b'app-sidebar' not in res_login.data

    res_reg = client.get('/register')
    assert res_reg.status_code == 200
    assert b'Create Account' in res_reg.data
    assert b'app-sidebar' not in res_reg.data


def test_authenticated_pages_rendering(auth_client):
    """Authenticated users should receive 200 OK and sidebar on all dedicated pages."""
    pages = [
        ('/dashboard', b'Welcome back'),
        ('/workouts', b'Workout Sessions'),
        ('/progress', b'Progress'),
        ('/goals', b'Fitness Goals'),
        ('/calendar', b'Calendar'),
        ('/reports', b'Reports'),
        ('/profile', b'Profile')
    ]

    for path, expected_text in pages:
        res = auth_client.get(path)
        assert res.status_code == 200, f"Page {path} failed with {res.status_code}"
        assert expected_text in res.data, f"Page {path} missing expected content"
        assert b'app-sidebar' in res.data, f"Page {path} missing desktop sidebar"
        assert b'FitTrack' in res.data


def test_root_redirect_for_authenticated_user(auth_client):
    """Root URL / should redirect authenticated users to /dashboard."""
    res = auth_client.get('/', follow_redirects=False)
    assert res.status_code == 302
    assert '/dashboard' in res.headers.get('Location', '')
