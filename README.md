[![Docker Pulls](https://img.shields.io/docker/pulls/bodastage/bts-ce-api.svg)]() [![Docker Automated build](https://img.shields.io/docker/automated/bodastage/bts-ce-api.svg)]() [![Docker Build Status](https://img.shields.io/docker/build/bodastage/bts-ce-api.svg)]() [![license](https://img.shields.io/github/license/bodastage/bts-ce-api.svg)](https://github.com/bodastage/bts-ce-api/blob/master/LICENCE) 

## Boda Telecom Suite  REST API
REST API for Boda Telecom Suite Communtiy Edition (BTS-CE). BTS-CE is an open source telecommunication network management platform.

## Built With
- [Python](https://www.python.org)
- [Flask](http://flask.pocoo.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/)

## Running
* 
```
# Install dependencies
pip install -r requirements.txt 

# Set Database connection details
export BTS_DB_USER=bodastage
export BTS_DB_PASS=password
export BTS_DB_HOST=localhost
export BTS_DB_PORT=5432
export BTS_DB_NAME=bts

# Run server
python run.py 

#
python run.py --port=<PORT> --server=<HOST IP>
```
*

## Running docker container manually

### Dockerhub container registry
```
docker run \
--name bts-ce-api \
-e BTS_DB_HOST='192.168.99.100' \
-e BTS_DB_NAME='bts' \
-e BTS_DB_USER='bodastage' \
-e BTS_DB_PASS='password' \
-e BTS_DB_PORT='5432' \
-v `pwd`:/app \
-p 8181:8181 bts-ce-api
```

### Gitlab container registry
```
docker run \
--name bts-ce-api \
-e BTS_DB_HOST='192.168.99.100' \
-e BTS_DB_NAME='bts' \
-e BTS_DB_USER='bodastage' \
-e BTS_DB_PASS='password' \
-e BTS_DB_PORT='5432' \
-v `pwd`:/app \
-p 8181:8181 registry.gitlab.com/bts-ce/bts-ce-api
```

## Resources

* [Online Documentation](http://docs.bodastage.com)

## Copyright / License
Copyright 2017 - 2019 [Bodastage Solutions](http://www.bodastage.com)

Licensed under the Apache License, Version 2.0 ; you may not use this work except in compliance with the License. You may obtain a copy of the License in the LICENSE file, or at:

https://www.apache.org/licenses/LICENSE-2.0

