#!/bin/sh
python manage.py migrate
python manage.py collectstatic
python manage.py import_json -f data/tags.json -a recipes -m Tag
python manage.py import_json -f data/ingredients.json -a recipes -m Ingredient
cp -r /app/collected_static/. /backend_static/static/
gunicorn --bind 0.0.0.0:8000 main.wsgi