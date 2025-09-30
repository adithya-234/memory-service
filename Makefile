.PHONY: run-local ssh-local build test clean

# Default target
default: help

# Help target
help:
	@echo "Available targets:"
	@echo "  run-local    - Run the application locally using Docker Compose"
	@echo "  stop-local   - Stop the running containers without removing them"
	@echo "  ssh-local    - SSH into the running Docker container"
	@echo "  build        - Build the Docker image"
	@echo "  test         - Run tests"
	@echo "  clean        - Stop and remove containers"

# Run the application locally using Docker Compose
run-local:
	docker-compose up -d
	@echo "Memory service is starting..."
	@echo "Check status with: docker-compose ps"
	@echo "View logs with: docker-compose logs -f"
	@echo "Service will be available at: http://localhost:8000"

# SSH into the running Docker container
ssh-local:
	@if [ -z "$$(docker-compose ps -q memory-service)" ]; then \
		echo "Error: memory-service container is not running. Run 'make run-local' first."; \
		exit 1; \
	fi
	docker-compose exec memory-service /bin/bash

# Build the Docker image
build:
	docker-compose build

# Run tests
test:
	docker-compose run --rm memory-service pytest

# Stop the running containers without removing them
stop-local:
	@if [ -z "$(docker-compose ps -q)" ]; then \
		echo "No running containers found."; \
		exit 0; \
	fi
	docker-compose stop
	@echo "Containers stopped (but not removed)"

# Stop and remove containers
clean:
	docker-compose down
	@echo "Containers stopped and removed"