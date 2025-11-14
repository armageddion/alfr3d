#!/bin/bash

# Linting script for Alfr3d project

echo "Running linting on all services..."

# Frontend (Node.js)
echo "Linting service_frontend..."
cd services/service_frontend
npm run lint

# API service
echo "Linting service_api..."
cd ../service_api
flake8 app.py --max-line-length=100 --ignore=E203,W503
black --check --diff app.py

# Daemon service
echo "Linting service_daemon..."
cd ../service_daemon
flake8 alfr3ddaemon.py daemon.py utils/ --max-line-length=100 --ignore=E203,W503
black --check --diff alfr3ddaemon.py daemon.py utils/

# User service
echo "Linting service_user..."
cd ../service_user
flake8 app.py --max-line-length=100 --ignore=E203,W503
black --check --diff app.py

# Device service
echo "Linting service_device..."
cd ../service_device
flake8 app.py --max-line-length=100 --ignore=E203,W503
black --check --diff app.py

# Environment service
echo "Linting service_environment..."
cd ../service_environment
flake8 environment.py weather_util.py --max-line-length=100 --ignore=E203,W503
black --check --diff environment.py weather_util.py

echo "Linting complete."