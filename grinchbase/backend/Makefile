protoc := python3 -m grpc_tools.protoc

build: grinchbase_pb2_grpc.py grinchbase_pb2.py
	@echo Build done.

grinchbase_pb2_grpc.py grinchbase_pb2.py: ../grinchbase.proto
	$(protoc) --python_out=. --grpc_python_out=. -I .. ../grinchbase.proto

run: build
	python server.py

clean:
	rm -rf grinchbase_pb2_grpc.py grinchbase_pb2.py __pycache__

.PHONY: build run clean
