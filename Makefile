.PHONY: build run-local stop-local ssh-local

# Build the Docker image
build:
	docker build -t memory-service .

# Run the service locally with Docker
run-local:
	docker run -d -p 8000:8000 --name memory-service memory-service

# Stop the local service
stop-local:
	docker stop memory-service && docker rm memory-service

# SSH into the running container
ssh-local:
	docker exec -it memory-service /bin/bash
