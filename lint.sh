#!/bin/bash

# Linting script for Alfr3d project

echo "Running linting on Python services..."

# Frontend
echo "Linting service_frontend..."
cd services/service_frontend
flake8 app/ tests/ --max-line-length=100 --ignore=E203,W503
black --check --diff app/ tests/

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