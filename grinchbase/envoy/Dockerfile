FROM envoyproxy/envoy-dev
COPY ./envoy.yaml /etc/envoy/envoy.yaml
COPY serverkey.pem /serverkey.pem
COPY servercert.pem /servercert.pem
CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
