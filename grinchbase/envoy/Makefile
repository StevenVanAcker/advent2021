cn := myenvoy

build: envoy.yaml
	docker build -t $(cn) .

run: build
	docker run -p 8080:8080 -p 9901:9901 --network=host $(cn)

.PHONY: build
