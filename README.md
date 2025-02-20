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
- User management
- Borrowed books tracking
- Book availability monitoring

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
- Python 3.8+
- PostgreSQL
- Redis

### Installation
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

### Running with Docker
```bash
docker-compose up --build
```

### Running Tests
```bash
pytest
```

## API Documentation
After running the services, API documentation will be available at:
- Frontend API: http://localhost:8000/docs
- Admin API: http://localhost:8001/docs

## License
MIT
