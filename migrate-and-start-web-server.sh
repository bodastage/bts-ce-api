#!/bin/bash

set -x 

export FLASK_APP=wait_for_database.py
flask run --host=0.0.0.0 --port=8181 &

# Wait abit for the database to startup
sleep 200

cd /migrations

source /python37/bin/activate
#Run migrations
alembic upgrade head
deactivate

# Stop the wait for database service 
pid=$(ps -ef | grep "flask run " | grep -v grep | awk '{print $2}')
kill -9 $pid 
unset FLASK_APP

cd /app
#Start api service
/usr/bin/gunicorn --config /app/gunicorn_config.py wsgi:app
