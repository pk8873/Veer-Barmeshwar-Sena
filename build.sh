#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Optional first-deploy admin bootstrap. Set DJANGO_ADMIN_USERNAME and
# DJANGO_ADMIN_PASSWORD temporarily in Render Environment settings.
python manage.py bootstrap_admin_from_env
