docker-build:
	docker buildx build --push --platform linux/arm64 --build-arg ARCH=linux/arm64 -t weaxme/pet-project:reddit-agent-latest .