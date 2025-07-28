docker-build:
	docker buildx build --push --platform linux/arm64 --build-arg ARCH=linux/arm64 -t weaxme/pet-project:reddit-agent-latest .

docker-build-macos:
	docker buildx build --load --platform darwin/arm64 --build-arg ARCH=darwin/arm64 -t weaxme/pet-project:reddit-agent-latest-macos .