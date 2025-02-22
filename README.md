# Library Management System

A distributed library management system built with FastAPI and PostgreSQL. The system consists of two independent microservices:

1. Frontend API - Handles user-facing operations like book browsing and borrowing
2. Admin API - Manages administrative operations like book management and user oversight

## Features

### Frontend API
- User enrollment
- Book catalogue browsing
- Book filtering by publisher and category
- Book borrowing system

### Admin API
- Book catalogue management
- User oversight
- Borrowed books tracking
- User creation broadcasting via RabbitMQ

## Tech Stack
- FastAPI - Modern, fast web framework for building APIs
- PostgreSQL - Primary database
- Docker - Containerization
- pytest - Testing framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- Redis - For service communication

## Project Structure
```
library_system/
├── docker/
│   ├── frontend/
│   │   └── Dockerfile
│   └── admin/
│       └── Dockerfile
├── frontend_api/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── books.py
│   │   │   │   ├── users.py
│   │   │   │   ├── borrow.py
│   │   │   │   └── health.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── book.py
│   │   │   ├── user.py
│   │   │   └── borrow.py
│   │   ├── schemas/
│   │   │   ├── book.py
│   │   │   ├── user.py
│   │   │   └── borrow.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── book_service.py
│   │       ├── book_sync_service.py
│   │       ├── borrow_service.py
│   │       └── user_service.py
│   └── tests/
├── admin_api/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── books.py
│   │   │   │   ├── users.py
│   │   │   │   ├── borrow.py
│   │   │   │   └── health.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── book.py
│   │   │   ├── user.py
│   │   │   └── borrow.py
│   │   ├── schemas/
│   │   │   ├── book.py
│   │   │   ├── user.py
│   │   │   └── borrow.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── book_service.py
│   │       ├── book_sync_service.py
│   │       ├── borrow_service.py
│   │       └── user_service.py
│   └── tests/
├── shared/
│   ├── message_broker.py
│   ├── message_types.py
│   └── pagination.py
├── docker-compose.yml
└── requirements.txt
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15
- RabbitMQ

### Development Setup
1. Clone the repository
2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Local Development
```bash
# Start the services in development mode
docker-compose up --build

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart <service_name>

# Stop all services
docker-compose down
```

### Mock Data for Testing
The project includes a script to generate mock data for testing the distributed library management system. This script demonstrates the inter-service communication and data synchronization between the frontend and admin services.

#### Setting up the Mock Data Script

1. Copy the mock data script to the container:
```bash
# Create the scripts directory in the container if it doesn't exist
docker compose exec frontend_api mkdir -p /app/scripts

# Copy the mock data script from your local machine to the container
docker compose cp scripts/mock_data.py frontend_api:/app/scripts/
```

2. Run the mock data script:
```bash
# Execute the script inside the frontend_api container
docker compose exec frontend_api python /app/scripts/mock_data.py
```

#### Data Creation and Synchronization
The script demonstrates the distributed nature of the system by:

1. **User Creation Flow**:
   - Creates users through the Frontend API
   - Frontend API publishes user creation events to RabbitMQ
   - Admin API consumes these events and synchronizes its user database
   - Result: Users exist in both services' databases

2. **Book Creation Flow**:
   - Creates books through the Admin API's bulk endpoint
   - Admin API publishes book creation events to RabbitMQ
   - Frontend API consumes these events and synchronizes its book catalogue
   - Result: Books are available in both services' databases

#### Sample Data Created
The script generates:
- 3 sample users:
  - john.doe2@example.com
  - jane.smith2@example.com
  - bob.wilson2@example.com
- 7 books across different categories (technology, business, fiction, etc.)

#### Verification Endpoints
You can verify the successful data creation and synchronization using these endpoints:

1. Frontend API:
   - List all available books: `GET /api/v1/books/`
   - Demonstrates successful book sync from Admin API

2. Admin API:
   - List users enrolled in the library: `GET /api/v1/users/`
   - Demonstrates successful user sync from Frontend API

The script includes comprehensive logging to track the creation and synchronization process, helping diagnose any potential issues in the distributed system.

### Production Deployment
1. Configure environment variables:
```bash
# Frontend API
export POSTGRES_USER=<postgres_user>
export POSTGRES_PASSWORD=<postgres_password>
export POSTGRES_SERVER=<postgres_server>
export POSTGRES_DB=<postgres_db>


# Admin API
export POSTGRES_USER=<postgres_user>
export POSTGRES_PASSWORD=<postgres_password>
export POSTGRES_SERVER=<postgres_server>
export POSTGRES_DB=<postgres_db>

```

2. Build and start services:
```bash
# Build images
docker-compose build --no-cache

# Start services in detached mode
docker-compose up -d

# Verify services are running
docker-compose ps
```

3. Health check endpoints:
```bash
# Frontend API
curl http://localhost:8000/api/v1/health

# Admin API
curl http://localhost:8001/api/v1/health
```

### Running Tests

The project has both unit and integration tests for each API service. Unit tests focus on testing individual components in isolation, while integration tests verify the interaction between different parts of the system.

#### Test Dependencies
First, install the required test packages:
```bash
# Install test dependencies inside the container
docker compose exec frontend_api pip install pytest-cov pytest-asyncio

# For admin API
docker compose exec admin_api pip install pytest-cov pytest-asyncio
```

#### Frontend API Tests
```bash
# Run all frontend tests
docker compose exec frontend_api pytest -v

# Run only unit tests
docker compose exec frontend_api pytest tests/unit -v

# Run only integration tests
docker compose exec frontend_api pytest tests/integration -v

# Run with coverage report
docker compose exec frontend_api pytest --cov=app --cov-report=term-missing tests/
```

#### Admin API Tests
```bash
# Run all admin tests
docker compose exec admin_api pytest -v

# Run only unit tests
docker compose exec admin_api pytest tests/unit -v

# Run only integration tests
docker compose exec admin_api pytest tests/integration -v

# Run with coverage report
docker compose exec admin_api pytest --cov=app --cov-report=term-missing tests/
```

## API Documentation

After running the services, interactive API documentation (Swagger UI) will be available at:
- Frontend API: http://localhost:8000/docs
- Admin API: http://localhost:8001/docs

### Frontend API Endpoints

#### Books
- `GET /api/v1/books/`
  - List all books with optional filtering
  - Query Parameters:
    - `skip` (int): Number of books to skip (pagination)
    - `limit` (int): Maximum number of books to return (1-1000)
    - `publisher` (string): Filter by publisher (e.g., PENGUIN, HARPER_COLLINS)
    - `category` (string): Filter by category (e.g., FICTION, NON_FICTION)
    - `available_only` (bool): Only show available books

- `GET /api/v1/books/{book_id}`
  - Get detailed information about a specific book
  - Response includes:
    - Book details (title, author, ISBN)
    - Current availability status
    - Expected return date (if borrowed)
    - Publisher and category information

- `GET /api/v1/books/publishers/`
  - Get list of all publishers
  - Returns: List of publisher names (e.g., ["PENGUIN", "HARPER_COLLINS"])

- `GET /api/v1/books/categories/`
  - Get list of all book categories
  - Returns: List of category names (e.g., ["FICTION", "NON_FICTION"])

#### Users
- `POST /api/v1/users/`
  - Create a new user account
  - Request Body:
    ```json
    {
        "email": "john.doe@example.com",
        "firstname": "John",
        "lastname": "Doe"
    }
    ```
  - Email must be unique

- `GET /api/v1/users/me/{user_id}`