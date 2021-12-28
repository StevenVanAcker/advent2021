protoc := protoc
npm := npm

package-lock.json: package.json
	$(npm) install

grinchbase_grpc_web_pb.js grinchbase_pb.js: ../grinchbase.proto
	$(protoc) -I .. ../grinchbase.proto --js_out=import_style=commonjs,binary:. --grpc-web_out=import_style=commonjs,mode=grpcwebtext:.

dist/main.js: index.js package-lock.json grinchbase_grpc_web_pb.js grinchbase_pb.js
	npm run build

install: dist/main.js
	cp dist/* extra/* /usr/share/nginx/html/

run: dist/main.js
	cd dist && python -m http.server

clean:
	rm -rf grinchbase*_pb.js node_modules/ package-lock.json dist/
