#!/bin/bash

# This script is run by Jenkins.

# settings.py disables some dependencies when this env variable is set.
export USING_DJANGO_TESTRUNNER=1

# Ensure a fresh DB available.
mysql -u root --password=MICrONS < fresh_db.sql

cd ../django

# Ensure migrations generated for a clean slate.
rm -rf */migrations

python3 manage.py makemigrations --noinput

# Force create migrations for the bosscore app.
python3 manage.py makemigrations bosscore --noinput 

python3 manage.py migrate

python3 manage.py collectstatic --noinput

python3 manage.py jenkins --enable-coverage --noinput

