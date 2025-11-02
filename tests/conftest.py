import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope="session")
def kafka_bootstrap_servers():
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

@pytest.fixture(scope="session")
def mysql_config():
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),  # Use localhost for tests outside docker
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "rootpassword"),
        "database": os.getenv("MYSQL_DATABASE", "alfr3d_db"),
    }

@pytest.fixture(scope="session")
def frontend_app():
    """Flask app fixture for frontend tests."""
    from services.service_frontend.app import app
    app.config['TESTING'] = True
    return app

@pytest.fixture(scope="session")
def frontend_client(frontend_app):
    """Flask test client for frontend tests."""
    return frontend_app.test_client()