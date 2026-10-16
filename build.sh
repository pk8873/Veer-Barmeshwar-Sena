#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Optional first-deploy admin bootstrap. Set DJANGO_ADMIN_USERNAME and
# DJANGO_ADMIN_PASSWORD temporarily in Render Environment settings.
python manage.py bootstrap_admin_from_env
# Idempotently publish the five sourced Hindi history posts when a staff user exists.
python manage.py seed_brahmeshwar_posts
