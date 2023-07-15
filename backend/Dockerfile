FROM python:3.9-slim-bullseye 
WORKDIR /app
COPY requirements.txt .
RUN pip install gunicorn==20.1.0
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod 700 migrate_collect_static_gunicorn.sh
ENTRYPOINT ["./migrate_collect_static_gunicorn.sh"]