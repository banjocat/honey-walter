FROM python:2

RUN pip install elasticsearch>=6.0.0
RUN pip install elastalert

RUN mkdir -p /etc/elastalert
RUN mkdir -p /etc/elastalert/rules/
COPY ./config.yml /etc/elastalert/config.yml
COPY ./rules /etc/elastalert/rules

CMD elastalert --config /etc/elastalert/config.yml
