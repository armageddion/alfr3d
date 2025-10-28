import pytest
from app.models import User, Device, Environment, States, UserTypes, DeviceTypes, Config, Quips, db

def test_user_creation(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.check_password('password')
        assert not user.check_password('wrong')

def test_device_creation(app):
    with app.app_context():
        device = Device(name='testdevice', IP='192.168.1.1', MAC='00:00:00:00:00:01')
        db.session.add(device)
        db.session.commit()

        assert device.id is not None

def test_environment_creation(app):
    with app.app_context():
        env = Environment(name='testenv', latitude=10.0, longitude=20.0)
        db.session.add(env)
        db.session.commit()

        assert env.id is not None

def test_states_creation(app):
    with app.app_context():
        state = States(state='test')
        db.session.add(state)
        db.session.commit()

        assert state.id is not None

def test_config_creation(app):
    with app.app_context():
        config = Config(name='test_config', value='test_value')
        db.session.add(config)
        db.session.commit()

        assert config.id is not None

def test_quips_creation(app):
    with app.app_context():
        quip = Quips(type='test', quips='Test quip')
        db.session.add(quip)
        db.session.commit()

        assert quip.id is not None