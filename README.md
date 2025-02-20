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
- Real-time book availability updates via Redis

### Admin API
- Book catalogue management
- User management
- Borrowed books tracking
- Book availability monitoring
- Book updates broadcasting via Redis

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
bookstore/
├── docker/
│   ├── frontend/
│   └── admin/
├── frontend_api/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── admin_api/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── docker-compose.yml
└── requirements.txt
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15
- Redis 7

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

### Production Deployment
1. Configure environment variables:
```bash
# Frontend API
export POSTGRES_USER=frontend_user
export POSTGRES_PASSWORD=<secure_password>
export POSTGRES_SERVER=frontend_db
export POSTGRES_DB=frontend_db
export REDIS_URL=redis://redis:6379/0

# Admin API
export POSTGRES_USER=admin_user
export POSTGRES_PASSWORD=<secure_password>
export POSTGRES_SERVER=admin_db
export POSTGRES_DB=admin_db
export REDIS_URL=redis://redis:6379/0
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
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage report
pytest --cov=app tests/
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
  - Get user information
  - Returns user's personal information and account creation timestamp

#### Borrowing
- `POST /api/v1/borrow/{user_id}/borrow/{book_id}`
  - Borrow a book
  - Query Parameters:
    - `days` (int): Number of days to borrow (1-30)
  - Responses:
    - 200: Successfully borrowed
    - 400: Book unavailable
    - 404: Book/User not found

### Admin API Endpoints

#### Books Management
- `POST /api/v1/books/`
  - Add a new book to the library
  - Requires book details including ISBN, title, author

- `PUT /api/v1/books/{book_id}`
  - Update book information
  - Can modify title, author, category, etc.

- `DELETE /api/v1/books/{book_id}`
  - Remove a book from the library

#### User Management
- `GET /api/v1/users/`
  - List all users
  - Supports pagination

- `GET /api/v1/users/{user_id}/borrows`
  - View user's borrowing history

#### Health Checks
- `GET /api/v1/health`
  - Check service health
  - Verifies database and Redis connections
  - Returns service status and uptime

### Error Responses
All endpoints follow a consistent error response format:
```json
{
    "detail": "Error message explaining what went wrong"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

## Monitoring and Maintenance

### Logs
```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs frontend_api

# Follow logs in real-time
docker-compose logs -f
```

### Database Management
```bash
# Access Frontend database
docker-compose exec frontend_db psql -U frontend_user -d frontend_db

# Access Admin database
docker-compose exec admin_db psql -U admin_user -d admin_db

# Create database backup
docker-compose exec frontend_db pg_dump -U frontend_user frontend_db > backup.sql
```

### Redis Management
```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Monitor Redis events
docker-compose exec redis redis-cli monitor
```

## License
MIT
