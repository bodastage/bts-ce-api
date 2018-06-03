#!/bin/bash

set -x 

cd /migrations

#Run migrations
alembic upgrade head 


cd /app
#Start webserver
/usr/bin/gunicorn --config /app/gunicorn_config.py wsgi:app