# Memory Service

A simple FastAPI service that allows users to store and retrieve personal memories. Think of it as a digital notepad where users can save things they want to remember and easily look them up later.

## Features

- **Memory Creation**: Store memories with content and automatic timestamp tracking
- **Memory Retrieval**: Get specific memories by ID
- **User Identification**: User-based memory storage with required UUID header
- **Service Information**: Root endpoint providing basic service details
- **In-memory storage**: Fast access with UUID-based indexing
- **RESTful API**: Clean API design with proper HTTP methods
- **Request Validation**: Structured MemoryRequest model for data validation
- **Testing Infrastructure**: Comprehensive unit test suite with pytest and fixtures

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd memory_service
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Local Development
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

#### Option 2: Docker
Build and run with Docker:
```bash
# Build the Docker image
docker build -t memory-service .

# Run the container
docker run -p 8000:8000 memory-service
```

#### Option 3: Docker Compose
Use Docker Compose for easier deployment:
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Docker Notes for macOS Users

- **Docker Desktop**: Ensure Docker Desktop is installed and running
- **Port Mapping**: The service will be available at `http://localhost:8000`
- **Memory Limits**: Docker Desktop on macOS may have memory limits - adjust in Docker Desktop settings if needed
- **Performance**: File system performance may be slower than native Linux - use Docker volumes for better performance if storing persistent data


### API Endpoints

- `GET /` - Root endpoint that returns service information
- `POST /memories` - Create a new memory (requires `user-id` header with UUID format)
- `GET /memories/{memory_id}` - Retrieve a specific memory by ID

### Testing

Run tests with:
```bash
pytest
```


## Project Goals

- Build a minimal but functional memory storage service
- Focus on simplicity and ease of use
- Provide reliable storage and retrieval of user memories