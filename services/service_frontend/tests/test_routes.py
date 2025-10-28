import pytest
from app.models import db, User

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_login_post_invalid(client):
    response = client.post('/login', data={'username': 'invalid', 'password': 'invalid'})
    assert response.status_code == 200  # Form re-rendered

def test_register_post(client, app):
    with app.app_context():
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password',
            'password2': 'password'
        })
        assert response.status_code == 302  # Redirect to login
        user = User.query.filter_by(username='newuser').first()
        assert user is not None

def test_logout(client, app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        with client:
            client.post('/login', data={'username': 'testuser', 'password': 'password'})
            response = client.get('/logout')
            assert response.status_code == 302