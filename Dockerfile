from python:2

RUN pip install --upgrade pip

COPY ./honey/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Directory format
RUN mkdir -p /app
WORKDIR /app
COPY ./honey/ /app

CMD python server.py

