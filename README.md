# Alfr3d

A containerized microservices project for home automation, featuring Kafka messaging, MySQL database, and Python services. Includes a Flask web frontend for user/device management.

## Features

- **Microservices Architecture**: Modular services for users, devices, environment, and frontend.
- **Messaging**: Kafka-based communication between services.
- **Database**: MySQL with optimized, secure queries.
- **Security**: Parameterized SQL queries to prevent injection; password hashing.
- **Performance**: Optimized DB calls with batch updates and reduced round trips.
- **Testing**: Comprehensive unit tests, route tests, and fuzz testing for robustness.
- **Containerization**: Docker Compose for local development; Kubernetes manifests for production.

## Services

- **Zookeeper**: Required for Kafka coordination.
- **Kafka**: Message broker with auto-created topics (`speak`, `environment`, `device`, `user`, `google`).
- **MySQL**: Database with schema aligned to application models.
- **Service User**: Manages users, handles online/offline status via device activity.
- **Service Device**: Manages devices, performs LAN scanning.
- **Service Environment**: Handles geolocation and weather updates.
- **Service Frontend**: Flask web app for user registration, login, device management, and posts.

## Setup

1. Ensure Docker and Docker Compose are installed.
2. Copy `.env.example` to `.env` and update environment variables (e.g., DB credentials, Kafka URLs).
3. Run `docker-compose up --build` to start all services.
4. Access the frontend at `http://localhost:8000`.

## Ports

- Kafka: 9092
- MySQL: 3306
- Service Frontend: 8000

## Testing

Run tests for the frontend service:

```bash
cd services/service_frontend
pip install -r requirements.txt
pytest
```

- **Unit Tests**: Model creation and validation.
- **Route Tests**: HTTP endpoints for login, registration, etc.
- **Fuzz Tests**: Random input generation to ensure crash-resistance.

## Linting

Run linting across all services:

```bash
./lint.sh
```

This checks code style with flake8 and formatting with black. Fix issues with:

```bash
black services/service_frontend/app/ services/service_frontend/tests/
# Repeat for other services
```

## Development

Modify Python services in `services/` directories. Key improvements:

- **SQL Security**: All queries use parameterized statements.
- **Optimizations**: Batch DB updates, single-query operations.
- **Logging**: Container-friendly stdout logging.
- **Models**: SQLAlchemy models aligned with `createTables.sql`.

Rebuild with `docker-compose up --build`.

## Kubernetes Deployment

The project includes Kubernetes manifests in the `k8s/` directory for container orchestration.

### Prerequisites
- Kubernetes cluster (e.g., Minikube, EKS, GKE)
- kubectl configured

### Deploy to Kubernetes

1. Build and push Docker images to a registry (e.g., Docker Hub):
    ```
    docker build -t alfr3d/service-user:latest services/service_user
    docker build -t alfr3d/service-device:latest services/service_device
    docker build -t alfr3d/service-environment:latest services/service_environment
    docker build -t alfr3d/service-frontend:latest services/service_frontend
    # Push all images
    ```

2. Apply the manifests:
   ```
   kubectl apply -f k8s/
   ```

3. Check status:
   ```
   kubectl get pods
   kubectl get services
   ```

4. Access the frontend via the Ingress (configure DNS or use port-forward):
   ```
   kubectl port-forward svc/service-frontend 8000:8000
   ```
   Then visit http://localhost:8000

Note: Update image names in YAML files to match your registry.