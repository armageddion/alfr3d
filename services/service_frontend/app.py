from flask import Flask, render_template, request, redirect, jsonify
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
import pymysql
import os
import logging
import sys
import psutil
from kubernetes import client, config
import requests
import time

app = Flask(__name__, static_folder='static')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

KAFKA_URL = os.environ['KAFKA_BOOTSTRAP_SERVERS']
DATABASE_HOST = 'mysql'  # Service name in docker-compose
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'alfr3d_db')
MYSQL_USER = os.environ.get('MYSQL_USER', 'user')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')

# =======================
# CONFIGURATION
# =======================
SERVICES = {
    "service_daemon": "http://service_daemon:8080/health",
    "service_device": "http://service_device:8080/health",
    "service_user": "http://service_user:8080/health",
    "service_environment": "http://service_environment:8080/health",
    "service_frontend": "http://service_frontend:8080/health",
}

# Kafka topic connections
# Each entry is: topic: (source_service, [destination_services])
KAFKA_TOPICS = {
    "speak": ("service_daemon", ["service_environment"]),
    "google": ("service_daemon", ["service_frontend"]),
    "user": ("service_daemon", ["service_user"]),
    "device": ("service_frontend", ["service_device", "service_user"]),
    "environment": ("service_daemon", ["service_environment"]),
}

DB_CONFIG = {
    "host": DATABASE_HOST,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": MYSQL_DATABASE
}

producer = None

def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])
            print("Connected to Kafka")
        except Exception as e:
            print("Failed to connect to Kafka")
            return None
    return producer

def get_container_health():
    # Since running in docker-compose, not k8s, mock or skip
    # For demo, return mock data based on SERVICES
    health = {}
    for service in SERVICES.keys():
        health[service] = {
            'status': 'Running',  # Assume running
            'cpu': round(0.1 + 0.1 * len(service), 2),  # Mock CPU
            'memory': round(50 + 10 * len(service), 2),  # Mock memory
            'storage': 'N/A'
        }
    return health

def get_system_metrics():
    # Local metrics for frontend container
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }

def get_kafka_details():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=[KAFKA_URL])
        topics = admin_client.list_topics()
        details = {'topics': []}
        for topic in topics:
            partitions = admin_client.describe_topics([topic])
            if partitions and topic in partitions:
                topic_desc = partitions[topic]
                details['topics'].append({
                    'name': topic,
                    'partitions': len(topic_desc.partitions)
                })
        # For consumer lag, need consumer groups, but simplified
        details['consumer_lag'] = 'Not implemented'  # Placeholder
        admin_client.close()
        return details
    except Exception as e:
        print(f"Failed to get Kafka details: {e}")
        return {}

def get_mysql_details():
    try:
        db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        cursor = db.cursor()
        # Connections
        cursor.execute("SHOW PROCESSLIST")
        connections = len(cursor.fetchall())
        # Query latency - simplified, average from performance_schema if available
        try:
            cursor.execute("SELECT AVG(timer_wait/1000000000) FROM performance_schema.events_statements_summary_by_digest WHERE schema_name = %s", (MYSQL_DATABASE,))
            result = cursor.fetchone()
            latency = result[0] if result and result[0] else 0
        except:
            latency = 'N/A'
        # Table errors - check for crashed tables or something
        try:
            cursor.execute("SHOW TABLE STATUS WHERE Engine IS NOT NULL")
            tables = cursor.fetchall()
            errors = sum(1 for table in tables if len(table) > 14 and table[14] == 'Error')  # Comment field
        except:
            errors = 'N/A'
        db.close()
        return {
            'connections': connections,
            'query_latency': latency,
            'table_errors': errors
        }
    except Exception as e:
        print(f"Failed to get MySQL details: {e}")
        return {}

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/dashboard')
def dashboard():
    # For now, serve the static dashboard template
    # TODO: Make this dynamic with real data
    return render_template('dashboard.html')

@app.route('/dashboard/data')
def dashboard_data():
    container_health = get_container_health()
    return jsonify({'container_health': container_health})


@app.route('/control')
def control():
    logger.info("Serving control page")
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()

    # Users
    cursor.execute("SELECT u.id, u.username, u.email, s.state, ut.type FROM user u JOIN states s ON u.state = s.id JOIN user_types ut ON u.type = ut.id")
    users = cursor.fetchall()

    # Devices
    cursor.execute("SELECT d.id, d.name, d.IP, s.state, dt.type, u.username FROM device d JOIN states s ON d.state = s.id JOIN device_types dt ON d.device_type = dt.id JOIN user u ON d.user_id = u.id")
    devices = cursor.fetchall()

    # Environment
    cursor.execute("SELECT id, name, city, country, latitude, longitude FROM environment")
    environments = cursor.fetchall()

    # Users list for dropdown
    cursor.execute("SELECT id, username FROM user")
    all_users = cursor.fetchall()

    # Device types for dropdown
    cursor.execute("SELECT id, type FROM device_types")
    device_types = cursor.fetchall()

    # User types for add user
    cursor.execute("SELECT id, type FROM user_types")
    user_types = cursor.fetchall()

    # Routines
    cursor.execute("SELECT id, name, time, CASE WHEN enabled = 1 THEN 'Yes' ELSE 'No' END FROM routines")
    routines = cursor.fetchall()

    db.close()

    return render_template('control.html', users=users, devices=devices, environments=environments, routines=routines, all_users=all_users, device_types=device_types, user_types=user_types)

@app.route('/command', methods=['POST'])
def command():
    cmd = request.form.get('command')
    logger.info(f"Command route called with cmd: {cmd}")
    p = get_producer()
    if p:
        print("Producer is available, sending command...")
        try:
            if cmd == 'check_location':
                p.send('environment', b'check location')
            elif cmd == 'check_weather':
                p.send('environment', b'check weather')
            elif cmd == 'scan_network':
                p.send('device', b'scan net')
            elif cmd == 'check_gmail':
                p.send('google', b'check gmail')
            p.flush()
            logger.info(f"Sent command '{cmd}' to Kafka topic 'environment'")
            return 'Command sent: ' + cmd
        except Exception as e:
            return 'Failed to send command: ' + str(e)
    else:
        return 'Failed to connect to Kafka'

@app.route('/users')
def users():
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Users', headers=['ID', 'Username', 'Email', 'Password Hash', 'About Me', 'State', 'Last Online', 'Environment ID', 'Type'], data=data)

@app.route('/devices')
def devices():
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT d.id, d.name, d.IP, d.MAC, s.state, d.last_online, e.name, dt.type, u.username FROM device d JOIN states s ON d.state = s.id JOIN device_types dt ON d.device_type = dt.id JOIN user u ON d.user_id = u.id JOIN environment e ON d.environment_id = e.id")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Devices', headers=['ID', 'Name', 'IP', 'MAC', 'State', 'Last Online', 'Environment', 'Device Type', 'Username'], data=data)

@app.route('/environment')
def environment():
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM environment")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Environment', headers=['ID', 'Name', 'Latitude', 'Longitude', 'City', 'State', 'Country', 'IP', 'Low', 'High', 'Description', 'Sunrise', 'Sunset'], data=data)

@app.route('/routines')
def routines():
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM routines")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Routines', headers=['ID', 'Name', 'Time', 'Enabled', 'Triggered', 'Environment ID'], data=data)

@app.route('/states')
def states():
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM states")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='States', headers=['ID', 'State'], data=data)

@app.route('/environment/edit', methods=['POST'])
def edit_environment():
    env_id = request.form.get('id')
    name = request.form.get('name')
    if not name:
        return 'Error: Name cannot be empty', 400
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE environment SET name = %s WHERE id = %s", (name, env_id))
        db.commit()
    except Exception as e:
        db.rollback()
        return f'Error updating environment: {str(e)}', 500
    finally:
        db.close()
    return redirect('/')

@app.route('/user/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    user_type = request.form.get('type', 'guest')
    if not username or not email:
        return 'Error: Username and email required', 400
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    try:
        # Check if username exists
        cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
        if cursor.fetchone():
            return 'Error: Username already exists', 400
        # Get ids
        cursor.execute("SELECT id FROM user_types WHERE type = %s", (user_type,))
        ut = cursor.fetchone()
        if not ut:
            return 'Error: Invalid user type', 400
        ut_id = ut[0]
        cursor.execute("SELECT id FROM states WHERE state = 'offline'")
        state_id = cursor.fetchone()[0]
        # Set default password
        password_hash = 'password'  # TODO: hash properly
        cursor.execute("INSERT INTO user (username, email, password_hash, state, type) VALUES (%s, %s, %s, %s, %s)", (username, email, password_hash, state_id, ut_id))
        db.commit()
    except Exception as e:
        db.rollback()
        return f'Error adding user: {str(e)}', 500
    finally:
        db.close()
    return redirect('/')

@app.route('/user/edit', methods=['POST'])
def edit_user():
    user_id = request.form.get('id')
    username = request.form.get('username')
    email = request.form.get('email')
    if not username or not email:
        return 'Error: Username and email required', 400
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE user SET username = %s, email = %s WHERE id = %s", (username, email, user_id))
        db.commit()
    except Exception as e:
        db.rollback()
        return f'Error updating user: {str(e)}', 500
    finally:
        db.close()
    return redirect('/')

@app.route('/user/delete', methods=['POST'])
def delete_user():
    user_id = request.form.get('id')
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        return f'Error deleting user: {str(e)}', 500
    finally:
        db.close()
    return redirect('/')

@app.route('/device/edit', methods=['POST'])
def edit_device():
    device_id = request.form.get('id')
    name = request.form.get('name')
    username = request.form.get('username')
    device_type = request.form.get('device_type')
    if not name or not username or not device_type:
        return 'Error: Name, Username and Device Type cannot be empty', 400
    db = pymysql.connect(host=DATABASE_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    try:
        # Check if username exists
        cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return f'Error: Username {username} not found', 400
        user_id = user[0]
        # Check if device_type exists
        cursor.execute("SELECT id FROM device_types WHERE type = %s", (device_type,))
        dt = cursor.fetchone()
        if not dt:
            return f'Error: Device type {device_type} not found', 400
        device_type_id = dt[0]
        cursor.execute("UPDATE device SET name = %s, user_id = %s, device_type = %s WHERE id = %s", (name, user_id, device_type_id, device_id))
        db.commit()
    except Exception as e:
        db.rollback()
        return f'Error updating device: {str(e)}', 500
    finally:
        db.close()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)