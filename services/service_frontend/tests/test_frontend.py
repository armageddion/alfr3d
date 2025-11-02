import pytest
import json
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    """Test client for Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFrontendRoutes:
    """Test frontend route functionality."""

    def test_index_redirect(self, client):
        """Test that index redirects to dashboard."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/dashboard' in response.headers['Location']

    def test_dashboard_page(self, client):
        """Test dashboard page loads."""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'ALFR3D: Container Dashboard' in response.data

    def test_control_page(self, client):
        """Test control page loads."""
        response = client.get('/control')
        assert response.status_code == 200
        assert b'ALFR3D Control Panel' in response.data

    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.data == b'OK'


class TestDashboardDataAPI:
    """Test dashboard data API endpoints."""

    @patch('app.get_container_health')
    @patch('app.get_system_metrics')
    @patch('app.get_kafka_details')
    @patch('app.get_mysql_details')
    def test_dashboard_data_api(self, mock_mysql, mock_kafka, mock_system, mock_health, client):
        """Test dashboard data API returns proper structure."""
        # Mock the return values
        mock_health.return_value = {
            'service_daemon': {'status': 'healthy', 'cpu': 25.0, 'memory': 40.0},
            'service_environment': {'status': 'healthy', 'cpu': 15.0, 'memory': 30.0},
            'service_device': {'status': 'healthy', 'cpu': 20.0, 'memory': 35.0},
            'service_user': {'status': 'healthy', 'cpu': 18.0, 'memory': 28.0}
        }

        mock_system.return_value = {
            'cpu_percent': 35.5,
            'memory_percent': 45.2,
            'disk_percent': 60.1
        }

        mock_kafka.return_value = {
            'topics': [
                {'name': 'speak', 'partitions': 1},
                {'name': 'google', 'partitions': 1}
            ]
        }

        mock_mysql.return_value = {
            'connections': 5,
            'query_latency': 0.001,
            'table_errors': 0
        }

        response = client.get('/dashboard/data')
        assert response.status_code == 200

        data = json.loads(response.data)

        # Check that all expected services are present
        assert 'daemon' in data
        assert 'environment' in data
        assert 'frontend' in data
        assert 'device' in data
        assert 'mysql' in data
        assert 'user' in data

        # Check daemon service data
        assert data['daemon']['status'] == 'healthy'
        assert data['daemon']['cpu'] == 25.0
        assert data['daemon']['memory'] == 40.0

        # Check frontend uses system metrics
        assert data['frontend']['cpu'] == 35.5
        assert data['frontend']['memory'] == 45.2

        # Check MySQL data
        assert data['mysql']['connections'] == 5
        assert data['mysql']['tables'] == 8  # Default value

        # Check system metrics are included
        assert 'system' in data
        assert data['system']['cpu_percent'] == 35.5


class TestCommandAPI:
    """Test command sending functionality."""

    @patch('app.get_producer')
    def test_command_send_success(self, mock_get_producer, client):
        """Test successful command sending."""
        mock_producer = MagicMock()
        mock_get_producer.return_value = mock_producer

        response = client.post('/command', data={'command': 'check_location'})
        assert response.status_code == 200
        assert b'Command sent' in response.data

        # Verify producer was called
        mock_producer.send.assert_called_with('environment', b'check location')
        mock_producer.flush.assert_called_once()

    @patch('app.get_producer')
    def test_command_send_failure(self, mock_get_producer, client):
        """Test command sending failure."""
        mock_get_producer.return_value = None

        response = client.post('/command', data={'command': 'check_location'})
        assert response.status_code == 200
        assert b'Failed to connect to Kafka' in response.data

    def test_invalid_command(self, client):
        """Test invalid command handling."""
        response = client.post('/command', data={'command': 'invalid_command'})
        # Should still return success but not send anything
        assert response.status_code == 200


class TestUserManagement:
    """Test user management endpoints."""

    @patch('app.pymysql.connect')
    def test_users_page(self, mock_connect, client):
        """Test users page loads."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('user1', 'email1@test.com')]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.get('/users')
        assert response.status_code == 200
        assert b'Users' in response.data

    @patch('app.pymysql.connect')
    def test_user_add_success(self, mock_connect, client):
        """Test successful user addition."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]  # user_types id
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.post('/user/add', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'type': 'guest'
        })
        assert response.status_code == 302  # Redirect after success

    def test_user_add_missing_data(self, client):
        """Test user addition with missing data."""
        response = client.post('/user/add', data={'username': 'testuser'})
        assert response.status_code == 400
        assert b'Username and email required' in response.data


class TestDeviceManagement:
    """Test device management endpoints."""

    @patch('app.pymysql.connect')
    def test_devices_page(self, mock_connect, client):
        """Test devices page loads."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('device1', '192.168.1.1')]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.get('/devices')
        assert response.status_code == 200
        assert b'Devices' in response.data


class TestEnvironmentManagement:
    """Test environment management endpoints."""

    @patch('app.pymysql.connect')
    def test_environment_page(self, mock_connect, client):
        """Test environment page loads."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('env1', 'Test City')]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.get('/environment')
        assert response.status_code == 200
        assert b'Environment' in response.data


class TestRoutinesManagement:
    """Test routines management endpoints."""

    @patch('app.pymysql.connect')
    def test_routines_page(self, mock_connect, client):
        """Test routines page loads."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('routine1', '08:00')]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.get('/routines')
        assert response.status_code == 200
        assert b'Routines' in response.data


class TestStatesManagement:
    """Test states management endpoints."""

    @patch('app.pymysql.connect')
    def test_states_page(self, mock_connect, client):
        """Test states page loads."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, 'online')]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.get('/states')
        assert response.status_code == 200
        assert b'States' in response.data