FROM ubuntu:xenial

RUN apt-get update

RUN apt-get install -y cmake
RUN apt-get install -y libssl-dev
RUN apt-get install -y build-essential
RUN apt-get install -y libssh-dev




RUN mkdir -p /app


COPY . /app/.



WORKDIR /app
RUN cmake .
RUN make
WORKDIR /app/bin

CMD ["./honeywalter"]


