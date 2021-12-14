#!/bin/sh

poetry run python manage.py migrate --no-input

exec "$@"