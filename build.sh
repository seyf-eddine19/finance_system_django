#!/usr/bin/env bash
set -o errexit  # Exit script on error

# Install dependencies
pip install --upgrade pip  # Ensure latest pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate --no-input

# Run the script to create superuser
python createsuperuser.py
