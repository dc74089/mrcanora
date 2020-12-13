#!/usr/bin/env bash

pip3 install -r /app/code/requirements.txt;
python3 /app/code/manage.py migrate;
python3 /app/code/manage.py collectstatic --no-input;

exec gunicorn -b unix:/app/bind/gunicorn.sock -w ${WORKERS} ${WSGI_NAME}.wsgi;
