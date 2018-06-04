#!/bin/bash

set -x 

# Wait abit for the database to startup
sleep 10

cd /migrations

#Run migrations
alembic upgrade head 


cd /app
#Start webserver
/usr/bin/gunicorn --config /app/gunicorn_config.py wsgi:app