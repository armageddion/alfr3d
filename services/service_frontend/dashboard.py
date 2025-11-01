# dashboard.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import mysql.connector
import requests, psutil, time

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
    "host": "mysql",
    "user": "root",
    "password": "yourpassword",
    "database": "alfr3d_db"
}

# =======================
# HEALTH CHECK FUNCTIONS
# =======================
def check_mysql_health():
    try:
        start = time.time()
        conn = mysql.connector.connect(**DB_CONFIG)
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

# =======================
# DASH APP LAYOUT
# =======================
app = dash.Dash(__name__)

app.layout = html.Div(
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
