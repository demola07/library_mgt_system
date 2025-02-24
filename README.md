# Library Management System

A distributed library management system built with FastAPI, PostgreSQL and RabbitMQ. The system consists of two independent microservices and a shared folder to hold shared files between the two services:

1. Frontend API - Handles user-facing operations like book browsing and borrowing
2. Admin API - Manages administrative operations like book management and user oversight
3. Shared - Shared components like message broker, message types, pagination, etc.


### Video Demonstration

For a visual overview of the Library Management System, you can watch the video demonstration. This video provides insights into the project setup, as well as the system's features and functionalities, showcasing the Frontend and Admin APIs.

Here is a link to a <a href="https://drive.google.com/file/d/1KMo-8qMBhD3O_LQNDaKhbEbevHjsS3jJ/view?usp=sharing" target="_blank">video demonstration of the project</a>.
## Features

### Frontend API
- User enrollment and broadcasting via RabbitMQ
- Book catalogue browsing
- Book filtering by publisher and category
- Book borrowing system

### Admin API
- Book catalogue management
- User oversight
- Borrowed books tracking

## Tech Stack
- FastAPI - Modern, fast web framework for building APIs
- PostgreSQL - Primary database
- Docker - Containerization
- pytest - Testing framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- RabbitMQ - Message Communication

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
│   │   │   ├── routes/
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
│   │   ├── unit/
│   │   │   ├── test_book_service.py
│   │   │   ├── test_borrow_service.py
│   │   │   └── test_user_service.py
│   │   │   └── conftest.py
│   │   ├── integration/
│   │   │   ├── test_book_integration.py
│   │   │   ├── test_borrow_integration.py
│   │       └── conftest.py
│   │
|   |___ .env
|   
├── admin_api/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
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
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── book.py
│   │   │   ├── user.py
│   │   │   └── borrow.py
│   │   │   └── __init__.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── book_service.py
│   │       ├── book_sync_service.py
│   │       ├── borrow_service.py
│   │       └── user_service.py
│   └── tests/
│   │   ├── unit/
│   │   │   ├── test_book_service.py
│   │   │   ├── test_borrow_service.py
│   │   │   └── test_user_service.py
│   │   │   └── conftest.py
│   │   ├── integration/
│   │   │   ├── test_book_routes.py
│   │   │   ├── test_user_routes.py
│   │   │   └── conftest.py
│   │
|   |___ .env
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

### Development Setup with Docker

1. Clone the repository:

```bash
git clone https://github.com/demola07/library_mgt_system
```

2. Change into the repository directory:

```bash
cd library_mgt_system
```

3. Configure Environment Variables:

- Rename the `.env.example` file to `.env` in both the `frontend_api` and `admin_api` directories:

```bash
mv frontend_api/.env.example frontend_api/.env
mv admin_api/.env.example admin_api/.env
```

- Open each `.env` file and fill in the necessary environment variables as required for your setup.

4. Build and start the Docker containers:

```bash
docker-compose up --build
```

5. Access the application:

- The application should now be running and accessible at

  - frontend_api: `http://localhost:8000/api/v1/`
  - admin_api: `http://localhost:8001/api/v1/`

6. Stopping the containers:

- To stop the running containers, use:

```bash
docker-compose down
```

### Additional Notes

- Ensure Docker and Docker Compose are installed on your system.
- You can modify the `docker-compose.yml` file to change configurations as needed.

Health check endpoints:
```bash
# Frontend API
curl http://localhost:8000/api/v1/health

# Admin API
curl http://localhost:8001/api/v1/health
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

### Running Tests

The project has both unit and integration tests for each API service. Unit tests focus on testing individual components in isolation, while integration tests verify the interaction between different parts of the system.

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
- Frontend API: http://localhost:8000/api/v1/docs or http://localhost:8000/api/v1/redoc
- Admin API: http://localhost:8001/api/v1/docs or http://localhost:8001/api/v1/redoc

### Frontend API Endpoints

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

#### Books

- `GET /api/v1/books/`
  - List all available books with optional filtering
  - Query Parameters:
    - `skip` (int): Number of books to skip (pagination)
    - `limit` (int): Maximum number of books to return (1-1000)
    - `publisher` (string): Filter by publisher (e.g., PENGUIN, HARPER_COLLINS)
    - `category` (string): Filter by category (e.g., FICTION, NON_FICTION)

- `GET /api/v1/books/{book_id}`
  - et a single book by its ID
  - Response includes:
    - Book details (title, author, ISBN)
    - Publisher and category information

- `GET /api/v1/books/publishers/`
  - Get list of all publishers
  - Returns: List of publisher names (e.g., ["PENGUIN", "HARPER_COLLINS"])

- `GET /api/v1/books/categories/`
  - Get list of all book categories
  - Returns: List of category names (e.g., ["FICTION", "NON_FICTION"])

- `POST /api/v1/borrow/user/{user_id}/book/{book_id}?days=7`
  - Borrow book by ID (specify how long you want it for in days)
  - Query Parameter:
    - `days` (PositiveInt): How long you want to borrow book


### Admin API Endpoints

- `POST /api/v1/books/bulk`
  - Add new books to the catalogue
  - Request Body:
    ```json
    [
      {
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "isbn": "9780201633610",
        "publisher": "Addison-Wesley",
        "category": "Software Architecture"
      },
      {
        "title": "Deep Learning",
        "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
        "isbn": "9780262035613",
        "publisher": "MIT Press",
        "category": "Artificial Intelligence"
      }
    ]
    ```
  - isbn must be unique

- `DELETE /api/v1/books/{book_id}`
  - Remove a book from the catalogue.

- `GET /api/v1/users/`
  - Fetch/List users enrolled in the library.

- `GET /api/v1/users/borrowed-books`
  - Fetch/List users and the books they have borrowed

- `GET /api/v1/books/unavailable`
  - Fetch/List the books that are not available for borrowing (showing the day it will be available (return_date))
