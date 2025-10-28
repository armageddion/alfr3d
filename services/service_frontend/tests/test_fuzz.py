import pytest
from hypothesis import given, strategies as st
import string

@given(
    username=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation, min_size=0, max_size=100),
    email=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation, min_size=0, max_size=100),
    password=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation, min_size=0, max_size=100),
    password2=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation, min_size=0, max_size=100)
)
def test_register_fuzz(client, username, email, password, password2):
    """Fuzz test for registration endpoint with random inputs."""
    response = client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'password2': password2
    })
    # Should not crash, return some response
    assert response.status_code in [200, 302]

@given(
    username=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation, min_size=0, max_size=100),
    password=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation, min_size=0, max_size=100)
)
def test_login_fuzz(client, username, password):
    """Fuzz test for login endpoint with random inputs."""
    response = client.post('/login', data={
        'username': username,
        'password': password
    })
    # Should not crash
    assert response.status_code in [200, 302]

@given(
    body=st.text(alphabet=string.ascii_letters + string.digits + string.punctuation + '\n', min_size=0, max_size=500)
)
def test_post_fuzz(client, app, body):
    """Fuzz test for posting with random body."""
    with app.app_context():
        from app.models import User, db
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        with client:
            client.post('/login', data={'username': 'testuser', 'password': 'password'})
            response = client.post('/post', data={'post': body})
            # Should not crash
            assert response.status_code in [200, 302, 400]