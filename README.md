## Boda Telecom Suite Enterprise Edition REST API
REST API for Boda Telecom Suite Enterprise Edition (BTS-EE). BTS-EE is a telecommunication network management platform.


## Built With
- [Python](https://www.python.org)
- [Flask](http://flask.pocoo.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)

## Running docker container manually

### Running from gitlab container registry
```
docker run \
--name bts-ee-api \
-e BTS_DB_HOST='192.168.99.100' \
-e BTS_DB_DB='bts' \
-e BTS_DB_USER='bodastage' \
-e BTS_DB_PASS='password' \
-e BTS_DB_PORT='5432' \
-v `pwd`:/app \
-p 8181:8181 registry.gitlab.com/bts-ee/bts-ee-api
```

## Resources

* [Online Documentation](http://docs.bodastage.com)

## Copyright / License
Copyright 2017 - 2018 [Bodastage Solutions](http://www.bodastage.com)

Licensed under the Apache License, Version 2.0 ; you may not use this work except in compliance with the License. You may obtain a copy of the License in the LICENSE file, or at:

https://www.apache.org/licenses/LICENSE-2.0

“Commons Clause” License Condition v1.0

https://commonsclause.com/

