FROM ubuntu:16.04
LABEL maintainer Bodastage Engineering <engineering@bodastage.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python python-pip python-virtualenv gunicorn netcat git wget

# Setup flask application
RUN mkdir -p /deploy/
RUN mkdir -p /app
COPY ./requirements.txt /deploy/requirements.txt
RUN pip install -r /deploy/requirements.txt && pip install alembic
WORKDIR /app

# Install python 3.7
RUN mkdir /tmp/Python37 \
    && cd /tmp/Python37 \
    && wget https://www.python.org/ftp/python/3.7.1/Python-3.7.1.tgz \
    && tar xzf /tmp/Python37/Python-3.7.1.tar.xz \
    && cd /tmp/Python37/Python-3.7.1 \
    && ./configure \
    && sudo make altinstall \
    && pip3.7 -r /deploy/requirements.txt

# Create migrations folder
RUN mkdir -p /migrations && chmod -R 777  /migrations

COPY ./wait-for-it.sh /wait-for-it.sh
COPY ./migrate-and-start-web-server.sh /migrate-and-start-web-server.sh

RUN chmod 777 /wait-for-it.sh
RUN chmod 777 /migrate-and-start-web-server.sh 

EXPOSE 8181

# Start gunicorn
CMD ["/usr/bin/gunicorn", "--config", "/app/gunicorn_config.py", "wsgi:app"]
