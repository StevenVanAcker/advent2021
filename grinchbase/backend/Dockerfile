FROM ubuntu

RUN apt-get update && apt-get -y install python3 python3-pip make
RUN pip3 install grpcio-tools googleapis-common-protos pyyaml

COPY ./grinchbase.proto /opt
COPY ./backend/ /opt/backend

WORKDIR /opt/backend
RUN make

CMD python3 server.py
