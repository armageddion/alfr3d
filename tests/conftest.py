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
        "host": "localhost",  # Use localhost for tests outside docker
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "rootpassword"),
        "database": os.getenv("MYSQL_DATABASE", "alfr3d_db"),
    }