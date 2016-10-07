from python:2

# Apts
RUN apt-get update
RUN apt-get install -y python2.7-dev
RUN apt-get install -y autoconf
RUN apt-get install -y g++


# Pips
RUN pip install pycrypto
RUN pip install cryptography
RUN pip install twisted
RUN pip install PyYaml
RUN pip install voluptuous
RUN pip install python-logstash

# Directory format
RUN mkdir -p /app
WORKDIR /app
COPY ./honey/ /app

EXPOSE 2000
CMD python server.py

