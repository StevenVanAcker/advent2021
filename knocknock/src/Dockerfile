FROM ubuntu

RUN apt-get update && apt-get install -y python3

COPY flag.py /opt
COPY server.py /opt
ADD data /opt/data

USER nobody
WORKDIR /opt
CMD /opt/server.py
