import pytest
from app import create_app, db
from app.models import User, Device, Environment, States, UserTypes, DeviceTypes, Config, Quips
from config import Config

@pytest.fixture
def app():
    app = create_app(Config)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.app_context():
        db.create_all()
        # Seed some data
        state_online = States(state='online')
        state_offline = States(state='offline')
        db.session.add_all([state_online, state_offline])

        user_type = UserTypes(type='guest')
        db.session.add(user_type)

        device_type = DeviceTypes(type='guest')
        db.session.add(device_type)

        env = Environment(name='test', latitude=0, longitude=0)
        db.session.add(env)

        db.session.commit()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()