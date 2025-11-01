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
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import requests
import time

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
    "user": ("service_daemon", ["service_speak"]),
    "device": ("service_frontend", ["service_speak", "service_user"]),
    "environment": ("service_daemon", ["service_speak"]),
}

DB_CONFIG = {
    "host": DATABASE_HOST,
    "user": DATABASE_USER,
    "password": DATABASE_PSWD,
    "database": DATABASE_NAME
}

def check_mysql_health():
    try:
        start = time.time()
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables;")
        count = cursor.fetchone()[0]
        latency = (time.time() - start) * 1000
        conn.close()
        return {"status": "up", "tables": count, "latency": latency}
    except Exception as e:
        return {"status": "down", "error": str(e)}

def check_service_health(url):
    try:
        r = requests.get(url, timeout=1.5)
        if r.status_code == 200:
            return "up"
        else:
            return "warn"
    except:
        return "down"

producer = None

dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')

dash_app.layout = html.Div(
    style={"fontFamily": "Arial", "backgroundColor": "#0e1012", "color": "white", "padding": "20px"},
    children=[
        html.H2("System Health Dashboard", style={"textAlign": "center", "color": "#61dafb"}),
        dcc.Interval(id="update", interval=3000, n_intervals=0),

        # SERVICES + MYSQL
        html.Div(id="service-status", style={"display": "flex", "justifyContent": "space-around", "flexWrap": "wrap"}),
        html.Div(id="mysql-status", style={"marginTop": "30px"}),

        html.Hr(style={"marginTop": "40px", "borderColor": "#333"}),

        # KAFKA CONNECTION MAP
        html.Div([
            html.H3("Kafka Topic Connections", style={"color": "#61dafb", "textAlign": "center"}),
            html.Div(id="kafka-map", style={
                "position": "relative",
                "width": "100%",
                "height": "400px",
                "backgroundColor": "#1c1f24",
                "border": "1px solid #333",
                "borderRadius": "10px",
                "padding": "10px"
            })
        ]),

        html.Hr(style={"marginTop": "40px", "borderColor": "#333"}),

        # CPU GRAPH
        html.Div([
            html.H4("CPU Usage (%)"),
            dcc.Graph(id="cpu-graph", style={"height": "300px"})
        ])
    ]
)

@dash_app.callback(
    [Output("service-status", "children"),
     Output("mysql-status", "children"),
     Output("kafka-map", "children"),
     Output("cpu-graph", "figure")],
    [Input("update", "n_intervals")]
)
def update_dashboard(n):
    # Check services
    service_divs = []
    for name, url in SERVICES.items():
        status = check_service_health(url)
        color = {"up": "#27ae60", "warn": "#f1c40f", "down": "#e74c3c"}[status]
        glow = f"0 0 15px {color}"
        service_divs.append(html.Div(
            [
                html.H4(name, style={"textAlign": "center"}),
                html.Div("●", style={"fontSize": "50px", "color": color, "textShadow": glow, "textAlign": "center"}),
                html.Div(status.upper(), style={"textAlign": "center"})
            ],
            style={"width": "160px", "padding": "10px", "borderRadius": "10px", "background": "#1c1f24", "margin": "10px"}
        ))

    # MySQL
    db = check_mysql_health()
    db_color = "#27ae60" if db["status"] == "up" else "#e74c3c"
    mysql_div = html.Div([
        html.H3("MySQL Status", style={"color": "#61dafb"}),
        html.P(f"Status: {db['status'].upper()}", style={"color": db_color}),
        html.P(f"Tables: {db.get('tables', '—')}"),
        html.P(f"Latency: {db.get('latency', 0):.2f} ms"),
    ])

    # Kafka map - simple text representation
    kafka_divs = []
    for topic, (source, dests) in KAFKA_TOPICS.items():
        kafka_divs.append(html.Div([
            html.Strong(f"{source} → {topic} → {', '.join(dests)}")
        ], style={"margin": "5px"}))
    kafka_div = html.Div(kafka_divs)

    # CPU graph (animated)
    cpu_percent = psutil.cpu_percent()
    fig = {
        "data": [{"x": [time.strftime("%H:%M:%S")], "y": [cpu_percent],
                  "type": "bar", "marker": {"color": "#61dafb"}}],
        "layout": {"yaxis": {"range": [0, 100]}, "transition": {"duration": 300}}
    }

    return service_divs, mysql_div, kafka_div, fig

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
    try:
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        custom_api = client.CustomObjectsApi()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        health = {}
        # Get metrics if available
        try:
            metrics = custom_api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "pods")
            metrics_dict = {}
            for item in metrics['items']:
                pod_name = item['metadata']['name']
                namespace = item['metadata']['namespace']
                key = f"{namespace}/{pod_name}"
                cpu_total = 0
                memory_total = 0
                for container in item['containers']:
                    cpu_str = container['usage']['cpu']
                    if cpu_str.endswith('m'):
                        cpu_total += int(cpu_str[:-1]) / 1000  # milli-cores to cores
                    else:
                        cpu_total += float(cpu_str)
                    mem_str = container['usage']['memory']
                    if mem_str.endswith('Ki'):
                        memory_total += int(mem_str[:-2]) / 1024  # Ki to Mi
                    elif mem_str.endswith('Mi'):
                        memory_total += int(mem_str[:-2])
                    elif mem_str.endswith('Gi'):
                        memory_total += int(mem_str[:-2]) * 1024  # Gi to Mi
                    else:
                        memory_total += int(mem_str) / (1024 * 1024)  # assume bytes to Mi
                metrics_dict[key] = {'cpu': round(cpu_total, 2), 'memory': round(memory_total, 2)}
        except Exception as e:
            print(f"Metrics not available: {e}")
            metrics_dict = {}

        for pod in pods.items:
            if pod.metadata.namespace == 'default':  # assuming default namespace
                pod_name = pod.metadata.name
                key = f"default/{pod_name}"
                status = pod.status.phase
                cpu = metrics_dict.get(key, {}).get('cpu', 'N/A')
                memory = metrics_dict.get(key, {}).get('memory', 'N/A')
                # For storage, approximate with disk usage if local, else N/A
                storage = 'N/A'  # TODO: implement storage metrics
                health[pod_name] = {
                    'status': status,
                    'cpu': cpu,
                    'memory': memory,
                    'storage': storage
                }
        return health
    except Exception as e:
        print(f"Failed to get container health: {e}")
        return {}

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
            if partitions:
                part_info = partitions[0]
                details['topics'].append({
                    'name': topic,
                    'partitions': len(part_info.partitions)
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
        db = pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
        cursor = db.cursor()
        # Connections
        cursor.execute("SHOW PROCESSLIST")
        connections = len(cursor.fetchall())
        # Query latency - simplified, average from performance_schema if available
        cursor.execute("SELECT AVG(timer_wait/1000000000) FROM performance_schema.events_statements_summary_by_digest WHERE schema_name = %s", (DATABASE_NAME,))
        result = cursor.fetchone()
        latency = result[0] if result else 0
        # Table errors - check for crashed tables or something
        cursor.execute("SHOW TABLE STATUS WHERE Engine IS NOT NULL")
        tables = cursor.fetchall()
        errors = sum(1 for table in tables if table[14] == 'Error')  # Comment field
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
    container_health = get_container_health()
    system_metrics = get_system_metrics()
    kafka_details = get_kafka_details()
    mysql_details = get_mysql_details()
    return render_template('dashboard.html', container_health=container_health, system_metrics=system_metrics, kafka_details=kafka_details, mysql_details=mysql_details, kafka_topics=KAFKA_TOPICS)

@app.route('/dashboard/data')
def dashboard_data():
    container_health = get_container_health()
    return jsonify({'container_health': container_health})

@app.route('/control')
def control():
    logger.info("Serving control page")
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