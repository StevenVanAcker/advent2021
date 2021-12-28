FROM nginx:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install npm python3 make curl protobuf-compiler-grpc vim
RUN curl -Lo /usr/bin/protoc-gen-grpc-web https://github.com/grpc/grpc-web/releases/download/1.3.0/protoc-gen-grpc-web-1.3.0-linux-x86_64
RUN chmod +x /usr/bin/protoc-gen-grpc-web

COPY ./grinchbase.proto /opt
COPY ./frontend/ /opt/frontend
RUN make -C /opt/frontend install
