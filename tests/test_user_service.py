import pytest
import pymysql
from confluent_kafka import Producer
import time

def test_user_service_create_user(kafka_bootstrap_servers, mysql_config):
    """Test creating a user by sending Kafka message to user topic."""
    test_username = "test_user_service_123"

    # Clean up if exists
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE username = %s", (test_username,))
    conn.commit()
    cursor.close()
    conn.close()

    # Send create message
    producer = Producer({'bootstrap.servers': kafka_bootstrap_servers})
    producer.produce("user", key=b"create", value=test_username.encode('utf-8'))
    producer.flush()

    # Wait for service to process
    time.sleep(15)

    # Check DB
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = %s", (test_username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    assert user is not None, "User not created"
    assert user[1] == test_username, "Username mismatch"

    # Clean up
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE username = %s", (test_username,))
    conn.commit()
    cursor.close()
    conn.close()

def test_user_service_delete_user(kafka_bootstrap_servers, mysql_config):
    """Test deleting a user by sending Kafka message."""
    test_username = "test_user_delete_123"

    # First create user
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    # Get IDs
    cursor.execute("SELECT id FROM states WHERE state = 'offline'")
    state_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM user_types WHERE type = 'guest'")
    type_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM environment WHERE name = 'test'")
    env_id = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO user (username, last_online, state, type, environment_id) VALUES (%s, NOW(), %s, %s, %s)",
        (test_username, state_id, type_id, env_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    # Send delete message
    producer = Producer({'bootstrap.servers': kafka_bootstrap_servers})
    producer.produce("user", key=b"delete", value=test_username.encode('utf-8'))
    producer.flush()

    # Wait
    time.sleep(15)

    # Check deleted
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = %s", (test_username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    assert user is None, "User not deleted"