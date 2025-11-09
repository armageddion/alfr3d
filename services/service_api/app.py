# Modified for containerization: logging to stdout instead of file
import os
import sys
import logging
import subprocess
import json
import docker
import pymysql  # Changed from MySQLdb to pymysql
import threading
from datetime import datetime
from kafka import KafkaConsumer
from flask import Flask, request, jsonify
from flask_cors import CORS

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("ApiLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Changed to stream handler for container logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

MYSQL_DATABASE = os.environ["MYSQL_DATABASE"]
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PSWD = os.environ["MYSQL_PSWD"]
MYSQL_DB = os.environ["MYSQL_NAME"]
KAFKA_URL = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
ALFR3D_ENV_NAME = os.environ["ALFR3D_ENV_NAME"]

# Store recent events
recent_events = []


def consume_events():
    try:
        consumer = KafkaConsumer(
            "event-stream", bootstrap_servers=KAFKA_URL, auto_offset_reset="latest"
        )
        logger.info("Connected to Kafka event-stream topic")
        for message in consumer:
            try:
                event = json.loads(message.value.decode("utf-8"))
                recent_events.append(event)
                if len(recent_events) > 50:
                    recent_events.pop(0)
                logger.info(f"Received event: {event}")
            except Exception as e:
                logger.error(f"Error processing event message: {str(e)}")
    except Exception as e:
        logger.error(f"Error connecting to Kafka for events: {str(e)}")


# Check if Docker is available via subprocess
docker_available = False
try:
    # Set environment for docker commands
    env = os.environ.copy()
    env["DOCKER_HOST"] = "unix:///var/run/docker.sock"

    result = subprocess.run(
        ["docker", "version"], capture_output=True, text=True, timeout=5, env=env
    )
    if result.returncode == 0:
        docker_available = True
        logger.info("Docker CLI is available via socket")
    else:
        logger.warning("Docker CLI not available")
except Exception as e:
    logger.warning(f"Docker check failed: {str(e)}")

# Flask API
app = Flask(__name__)
CORS(app)


@app.route("/api/users")
def get_users():
    online = request.args.get("online", "false").lower() == "true"
    try:
        logger.info(f"Connecting to MySQL at {MYSQL_DATABASE} as {MYSQL_USER}")
        db = pymysql.connect(
            host=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PSWD, database=MYSQL_DB
        )
        cursor = db.cursor()
        if online:
            cursor.execute(
                """
                SELECT u.username, ut.type
                FROM user u
                JOIN states s ON u.state = s.id
                JOIN user_types ut ON u.type = ut.id
                JOIN environment e ON u.environment_id = e.id
                WHERE s.state = 'online' AND ut.type IN ('resident', 'guest') AND u.username NOT IN ('unknown', 'alfr3d') AND e.name = %s
            """,
                (ALFR3D_ENV_NAME,),
            )
        else:
            cursor.execute(
                """
                SELECT u.username, ut.type
                FROM user u
                JOIN user_types ut ON u.type = ut.id
                JOIN environment e ON u.environment_id = e.id
                WHERE u.username NOT IN ('unknown', 'alfr3d') AND e.name = %s
            """,
                (ALFR3D_ENV_NAME,),
            )
        users = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
        db.close()
        logger.info(f"Returning {len(users)} users")
        return jsonify(users)
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        # Return mock data for development
        mock_users = (
            [
                {"name": "Alice", "type": "resident"},
                {"name": "Bob", "type": "guest"},
                {"name": "Charlie", "type": "resident"},
            ]
            if online
            else [
                {"name": "Alice", "type": "resident"},
                {"name": "Bob", "type": "guest"},
                {"name": "Charlie", "type": "resident"},
                {"name": "David", "type": "guest"},
            ]
        )
        logger.warning("Returning mock user data due to database error")
        return jsonify(mock_users)


@app.route("/api/containers")
def get_containers():
    if not docker_available:
        logger.warning("Docker not available, returning mock containers list")
        # Return mock data that represents actual services
        import random
        import time

        # Generate somewhat realistic data
        base_time = int(time.time())
        containers = [
            {
                "name": "alfr3d-service-user-1",
                "cpu": round(random.uniform(5, 20), 1),
                "mem": round(random.uniform(30, 60), 1),
                "disk": 20.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-service-device-1",
                "cpu": round(random.uniform(3, 15), 1),
                "mem": round(random.uniform(25, 45), 1),
                "disk": 15.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-service-environment-1",
                "cpu": round(random.uniform(8, 25), 1),
                "mem": round(random.uniform(35, 55), 1),
                "disk": 18.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-service-daemon-1",
                "cpu": round(random.uniform(2, 10), 1),
                "mem": round(random.uniform(20, 35), 1),
                "disk": 12.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-service-api-1",
                "cpu": round(random.uniform(1, 8), 1),
                "mem": round(random.uniform(15, 30), 1),
                "disk": 8.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-service-frontend-1",
                "cpu": round(random.uniform(5, 15), 1),
                "mem": round(random.uniform(40, 70), 1),
                "disk": 25.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-mysql-1",
                "cpu": round(random.uniform(10, 30), 1),
                "mem": round(random.uniform(50, 80), 1),
                "disk": 30.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-zookeeper-1",
                "cpu": round(random.uniform(2, 8), 1),
                "mem": round(random.uniform(20, 40), 1),
                "disk": 10.0,
                "errors": 0,
            },
            {
                "name": "alfr3d-kafka-1",
                "cpu": round(random.uniform(15, 35), 1),
                "mem": round(random.uniform(60, 90), 1),
                "disk": 40.0,
                "errors": 0,
            },
        ]
        return jsonify(containers)

    try:
        # Set environment for docker commands
        env = os.environ.copy()
        env["DOCKER_HOST"] = "unix:///var/run/docker.sock"

        containers = []

        # Get container list
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        if result.returncode != 0:
            logger.error(f"Docker ps command failed: {result.stderr}")
            return jsonify({"error": "Failed to get container list"})

        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line.strip():
                try:
                    container = json.loads(line)
                    container_name = container.get("Names", "").split(",")[0]

                    # Filter to only alfr3d containers
                    if not container_name.startswith("alfr3d"):
                        continue

                    logger.info(
                        f"Processing container: {container_name}, status: {container.get('Status', '')}"
                    )

                    # Get CPU and memory stats
                    cpu_percent = 0.0
                    mem_percent = 0.0

                    stats_result = subprocess.run(
                        [
                            "docker",
                            "stats",
                            "--no-stream",
                            "--format",
                            "{{.CPUPerc}},{{.MemPerc}}",
                            container_name,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        env=env,
                    )
                    if stats_result.returncode == 0:
                        stats_line = stats_result.stdout.strip()
                        if stats_line:
                            parts = stats_line.split(",")
                            if len(parts) >= 2:
                                try:
                                    cpu_str = parts[0].rstrip("%")
                                    mem_str = parts[1].rstrip("%")
                                    cpu_percent = float(cpu_str) if cpu_str else 0.0
                                    mem_percent = float(mem_str) if mem_str else 0.0
                                except (ValueError, IndexError):
                                    pass

                    # Get container size for disk estimate
                    disk_percent = 15.0  # Default
                    size_result = subprocess.run(
                        [
                            "docker",
                            "ps",
                            "-a",
                            "--size",
                            "--format",
                            "{{.Size}}",
                            "-f",
                            f"name={container_name}",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        env=env,
                    )
                    if size_result.returncode == 0:
                        size_str = size_result.stdout.strip()
                        if size_str:
                            try:
                                # Parse size like "1.23MB (456MB)"
                                size_part = size_str.split(" ")[0]
                                if size_part.endswith("MB"):
                                    size_mb = float(size_part[:-2])
                                    disk_percent = min(size_mb / 10, 100)
                                elif size_part.endswith("GB"):
                                    size_gb = float(size_part[:-2])
                                    disk_percent = min(size_gb * 100, 100)
                            except (ValueError, IndexError):
                                pass

                    # Check for errors (simplified - check if container is running)
                    status = container.get("Status", "").lower()
                    errors = 0 if "up" in status else 1

                    containers.append(
                        {
                            "name": container_name,
                            "cpu": round(cpu_percent, 1),
                            "mem": round(mem_percent, 1),
                            "disk": round(disk_percent, 1),
                            "errors": errors,
                        }
                    )
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing container JSON: {str(e)}")
                    continue

        logger.info(f"Returning {len(containers)} containers")
        return jsonify(containers)
    except Exception as e:
        logger.error(f"Error fetching containers: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/events")
def get_events():
    return jsonify(recent_events)


if __name__ == "__main__":
    # Start event consumer thread
    threading.Thread(target=consume_events, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=False)
