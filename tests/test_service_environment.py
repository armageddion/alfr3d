import pytest
import sys
sys.path.append('../services/service_environment')
from unittest.mock import patch, MagicMock
import environment as env

@patch('services.service_environment.environment.urlopen')
@patch('services.service_environment.environment.pymysql.connect')
@patch('services.service_environment.environment.get_producer')
def test_checkLocation(mock_producer, mock_connect, mock_urlopen):
    """Test checkLocation function with mocked DB and API calls."""
    # Mock producer
    mock_prod = MagicMock()
    mock_producer.return_value = mock_prod

    # Mock DB connection
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_db
    mock_db.cursor.return_value = mock_cursor

    # Mock existing environment in DB
    mock_cursor.fetchone.return_value = (1, 'test', None, None, 'OldCity', 'OldState', 'OldCountry', 'oldip', None, None, None, None, None, None)

    # Mock IP fetch
    mock_ip_response = MagicMock()
    mock_ip_response.read.return_value.decode.return_value = '192.168.1.1'
    # Mock API response
    mock_api_response = MagicMock()
    mock_api_response.read.return_value.decode.return_value = '{"country_name": "NewCountry", "city": "NewCity", "ip": "192.168.1.1", "latitude": 10.0, "longitude": 20.0}'
    mock_urlopen.side_effect = [mock_ip_response, mock_api_response]

    # Call the function
    env.checkLocation()

    # Assert DB update was called with new data
    mock_cursor.execute.assert_any_call("UPDATE environment SET country = %s, state = %s, city = %s, IP = %s, latitude = %s, longitude = %s WHERE name = %s", ('NewCountry', 'NewCountry', 'NewCity', '192.168.1.1', '10.0', '20.0', 'test'))
    mock_db.commit.assert_called()

@patch('services.service_environment.environment.weather_util.getWeather')
@patch('services.service_environment.environment.pymysql.connect')
def test_checkWeather(mock_connect, mock_weather):
    """Test checkWeather function with mocked DB."""
    # Mock DB
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_db
    mock_db.cursor.return_value = mock_cursor

    # Mock environment with lat/long
    mock_cursor.fetchone.return_value = (1, 'test', 10.0, 20.0, 'City', 'State', 'Country', 'ip', None, None, None, None, None, None)

    # Call the function
    env.checkWeather()

    # Assert weather_util.getWeather was called with lat/long
    mock_weather.assert_called_with(10.0, 20.0)