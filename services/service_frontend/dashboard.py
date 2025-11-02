# dashboard.py
import os, time, math, random
from collections import deque
from typing import Dict, List, Tuple

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pymysql
import requests, psutil

# =======================
# CONFIGURATION
# =======================
CONTAINERS = [
    "service_daemon",
    "service_device",
    "service_user",
    "service_environment",
    "service_frontend",
    "mysql"
]

# Map logical positions in a 3x2 grid (col, row) -> pixel coordinates will be computed
GRID = {
    "service_daemon": (0, 0),
    "service_environment": (1, 0),
    "service_frontend": (2, 0),
    "service_device": (0, 1),
    "mysql": (1, 1),
    "service_user": (2, 1),
}

# Topics and orthogonal connections (source -> dest)
TOPICS = {
    "speak": ("service_daemon", "service_environment"),
    "google": ("service_daemon", "service_frontend"),
    "user": ("service_daemon", "service_user"),
    "device": ("service_frontend", "service_user"),
    "device_daemon": ("service_frontend", "service_daemon"),
    "environment": ("service_environment", "service_daemon")
}

# Visual sizes
NODE_W = 240
NODE_H = 120
PADDING_X = 80
PADDING_Y = 40

# Database configuration
DB_CONFIG = {
    "host": os.environ.get('MYSQL_DATABASE_URL', 'mysql'),
    "user": os.environ.get('MYSQL_USER', 'user'),
    "password": os.environ.get('MYSQL_PASSWORD', 'password'),
    "database": os.environ.get('MYSQL_DATABASE', 'alfr3d_db')
}

# =======================
# METRICS FUNCTIONS
# =======================
def get_container_metrics(name):
    """Get real metrics for containers"""
    try:
        if name == "mysql":
            # MySQL specific metrics
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Get connection count
            cursor.execute("SHOW PROCESSLIST")
            connections = len(cursor.fetchall())

            # Get some basic stats
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", (DB_CONFIG['database'],))
            tables = cursor.fetchone()[0]

            conn.close()

            return {
                "cpu": min(100, max(0, psutil.cpu_percent(interval=0.1))),
                "mem": min(100, max(0, psutil.virtual_memory().percent)),
                "restarts": 0,  # Would need container restart tracking
                "errors": 0,    # Would need error logging
                "connections": connections,
                "tables": tables,
                "health": "up" if connections > 0 else "warn"
            }
        else:
            # Generic container metrics - simplified
            return {
                "cpu": min(100, max(0, psutil.cpu_percent(interval=0.1))),
                "mem": min(100, max(0, psutil.virtual_memory().percent)),
                "restarts": 0,
                "errors": 0,
                "health": "up"  # Assume healthy for now
            }
    except Exception as e:
        return {
            "cpu": 0,
            "mem": 0,
            "restarts": 0,
            "errors": 1,
            "health": "down"
        }

def get_kafka_metrics(topic):
    """Get Kafka topic metrics - simplified"""
    return {
        "p": random.randint(0, 200),  # produce rate
        "c": random.randint(0, 180),  # consume rate
        "lag": random.randint(0, 50)  # lag
    }

# =======================
# LAYOUT HELPERS
# =======================
def grid_to_pixels(col, row):
    x = PADDING_X + col * (NODE_W + 80)
    y = PADDING_Y + row * (NODE_H + 60)
    return x, y

def orthogonal_path(src_px, dst_px):
    """Returns list of points for Manhattan/kinked path"""
    sx, sy = src_px
    dx, dy = dst_px
    mid_x = sx + (dx - sx) / 2
    start = (sx + NODE_W, sy + NODE_H/2)
    mid1 = (mid_x, sy + NODE_H/2)
    mid2 = (mid_x, dy + NODE_H/2)
    end = (dx, dy + NODE_H/2)
    return [start, mid1, mid2, end]

# =======================
# DASH APP
# =======================
app = dash.Dash(__name__, assets_folder="assets")
app.title = "ALFR3D Dashboard"

# Build node elements and precompute positions
NODE_POS = {}
nodes_html = []
for name in CONTAINERS:
    col, row = GRID[name]
    px, py = grid_to_pixels(col, row)
    NODE_POS[name] = (px, py)
    nodes_html.append(html.Div(
        id={"type": "node", "index": name},
        className="node-card",
        style={"left": f"{px}px", "top": f"{py}px", "width": f"{NODE_W}px", "height": f"{NODE_H}px"},
        children=[
            html.Div(name.replace("service_", "").replace("mysql", "MySQL"), className="node-title"),
            html.Div(className="node-health", id={"type": "node-health", "index": name}),
            html.Div(className="metrics-list", id={"type": "metrics", "index": name})
        ]
    ))

# Build lines (SVG polylines)
links_html = []
for topic, (src, dst) in TOPICS.items():
    if src in NODE_POS and dst in NODE_POS:
        src_px = NODE_POS[src]
        dst_px = NODE_POS[dst]
        pts = orthogonal_path(src_px, dst_px)
        links_html.append(
            html.Div([
                html.Span(topic, className="link-label"),
                html.P(
                    " ".join(f"{x},{y}" for x, y in pts),
                    hidden=True
                )
            ],
            id={"type": "link-svg", "index": topic},
            className="link-svg"
            )
        )

# Page layout
app.layout = html.Div(className="page", children=[
    html.H2("ALFR3D: Container Dashboard", className="page-title"),
    dcc.Interval(id="tick", interval=2000, n_intervals=0),
    html.Div(className="canvas", id="canvas", children=links_html + nodes_html),
    html.Div(className="legend", children=[
        html.Span("Legend:"),
        html.Span(className="legend-pill up"), html.Span("Healthy"),
        html.Span(className="legend-pill warn"), html.Span("Warning"),
        html.Span(className="legend-pill down"), html.Span("Down"),
    ])
])

# =======================
# CALLBACKS
# =======================
@app.callback(
    Output({"type": "metrics", "index": dash.dependencies.ALL}, "children"),
    Output({"type": "node-health", "index": dash.dependencies.ALL}, "style"),
    Input("tick", "n_intervals")
)
def update_metrics(n):
    all_metrics_children = []
    all_health_styles = []

    for name in CONTAINERS:
        m = get_container_metrics(name)

        # Create metric rows based on container type
        if name == "mysql":
            # MySQL specific metrics
            conn_bar = html.Div(className="metric-row", children=[
                html.Div("CONN", className="metric-name"),
                html.Div(className="metric-pill", children=str(m.get('connections', 0)))
            ])
            tables_bar = html.Div(className="metric-row", children=[
                html.Div("TBL", className="metric-name"),
                html.Div(className="metric-pill", children=str(m.get('tables', 0)))
            ])
            children = [conn_bar, tables_bar]
        else:
            # Generic container metrics
            cpu_bar = html.Div(className="metric-row", children=[
                html.Div("CPU", className="metric-name"),
                html.Div(className="metric-bar-bg", children=[
                    html.Div(className="metric-bar-fill", style={"width": f"{m['cpu']:.0f}%"})
                ]),
                html.Div(f"{m['cpu']:.0f}%", className="metric-value")
            ])
            mem_bar = html.Div(className="metric-row", children=[
                html.Div("MEM", className="metric-name"),
                html.Div(className="metric-bar-bg", children=[
                    html.Div(className="metric-bar-fill", style={"width": f"{m['mem']:.0f}%"})
                ]),
                html.Div(f"{m['mem']:.0f}%", className="metric-value")
            ])
            errors = html.Div(className="metric-row", children=[
                html.Div("ERR", className="metric-name"),
                html.Div(className="metric-pill", children=str(m['errors']))
            ])
            children = [cpu_bar, mem_bar, errors]

        all_metrics_children.append(children)

        # Health style
        color = {"up": "#27ae60", "warn": "#f1c40f", "down": "#e74c3c"}[m['health']]
        health_style = {"backgroundColor": color, "boxShadow": f"0 0 12px {color}"}
        all_health_styles.append(health_style)

    return all_metrics_children, all_health_styles

# =======================
# MAIN
# =======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    app.run(debug=True, host="0.0.0.0", port=port)
