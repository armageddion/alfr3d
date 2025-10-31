from flask import Flask, render_template, request, redirect
from kafka import KafkaProducer
import pymysql
import os
import logging
import sys

app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

KAFKA_URL = os.environ['KAFKA_BOOTSTRAP_SERVERS']
DATABASE_HOST = 'mysql'  # Service name in docker-compose
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'alfr3d_db')
DATABASE_USER = os.environ.get('DATABASE_USER', 'user')
DATABASE_PSWD = os.environ.get('DATABASE_PSWD', 'password')

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

@app.route('/')
def index():
    logger.info("Serving index page")
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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

    return render_template('index.html', users=users, devices=devices, environments=environments, routines=routines, all_users=all_users, device_types=device_types, user_types=user_types)

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
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Users', headers=['ID', 'Username', 'Email', 'Password Hash', 'About Me', 'State', 'Last Online', 'Environment ID', 'Type'], data=data)

@app.route('/devices')
def devices():
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT d.id, d.name, d.IP, d.MAC, s.state, d.last_online, e.name, dt.type, u.username FROM device d JOIN states s ON d.state = s.id JOIN device_types dt ON d.device_type = dt.id JOIN user u ON d.user_id = u.id JOIN environment e ON d.environment_id = e.id")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Devices', headers=['ID', 'Name', 'IP', 'MAC', 'State', 'Last Online', 'Environment', 'Device Type', 'Username'], data=data)

@app.route('/environment')
def environment():
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM environment")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Environment', headers=['ID', 'Name', 'Latitude', 'Longitude', 'City', 'State', 'Country', 'IP', 'Low', 'High', 'Description', 'Sunrise', 'Sunset'], data=data)

@app.route('/routines')
def routines():
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM routines")
    data = cursor.fetchall()
    db.close()
    return render_template('table.html', title='Routines', headers=['ID', 'Name', 'Time', 'Enabled', 'Triggered', 'Environment ID'], data=data)

@app.route('/states')
def states():
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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
    db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
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
    app.run(host='0.0.0.0', port=8000, debug=True)