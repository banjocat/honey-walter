from python:2


# Pips
RUN pip install pycrypto
RUN pip install cryptography
RUN pip install twisted
RUN pip install PyYaml
RUN pip install voluptuous
RUN pip install python-logstash
RUN pip install requests





# Directory format
RUN mkdir -p /app
WORKDIR /app
COPY ./honey/ /app

EXPOSE 2000
CMD python server.py

