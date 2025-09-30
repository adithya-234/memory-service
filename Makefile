.PHONY: build run-local stop-local ssh-local

# Build the Docker image
build:
	docker build -t memory-service .

# Run the service locally with Docker Compose
run-local:
	docker-compose up -d

# Stop the local service
stop-local:
	docker-compose down

# SSH into the running container
ssh-local:
	docker-compose exec memory-service /bin/bash