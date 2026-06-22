# FastAPI Backend Boilerplate

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0%2B-green.svg)](https://fastapi.tiangolo.com/)

A scalable, production-ready FastAPI backend boilerplate that standardizes authentication, asynchronous processing, event-driven workflows, real-time communication, and email services. Designed to accelerate the development of robust APIs and microservices.

## 🚀 Features

- **Authentication & Security**: JWT-based authentication with secure password hashing
- **Asynchronous Processing**: Celery integration for background task processing
- **Event-Driven Architecture**: Built-in support for event-driven workflows
- **Real-Time Communication**: WebSocket support for real-time features
- **Email Services**: Integrated email functionality for notifications and user communication
- **Database Management**: SQLAlchemy with Alembic migrations for robust data handling
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Validation**: Pydantic models for request/response validation
- **CI/CD Ready**: Jenkins pipeline configuration included
- **Docker Support**: Containerization ready with .dockerignore
- **OTP System**: Built-in OTP (One-Time Password) functionality

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL / SQLite (configurable)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Task Queue**: Celery + Redis
- **Validation**: Pydantic
- **Authentication**: JWT (JSON Web Tokens)
- **Email**: SMTP integration
- **Testing**: Pytest (ready for integration)
- **CI/CD**: Jenkins
- **Containerization**: Docker

## 📁 Project Structure

```
fastapi_boilerplate/
├── alembic/                 # Database migrations
├── api/                     # API routes and endpoints
├── core/                    # Core functionality (config, security)
├── db/                      # Database models and session management
├── pydanticValidators/      # Pydantic validation schemas
├── service/                 # Business logic services
├── util/                    # Utility functions (email, common helpers)
├── worker/                  # Celery worker configuration and tasks
├── main.py                  # Application entry point
├── Pipfile                  # Dependency management
├── alembic.ini             # Alembic configuration
├── Jenkinsfile             # CI/CD pipeline
└── example.env             # Environment variables template
```

## 🏁 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL or SQLite
- Redis (for Celery tasks)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fastapi-boilerplate.git
   cd fastapi-boilerplate
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Environment Setup**
   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

4. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   uvicorn main:app --reload
   ```

6. **Start Celery Worker** (in a separate terminal)
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## 🔧 Configuration

Key environment variables:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `REDIS_URL`: Redis connection URL
- `SMTP_SERVER`: Email server configuration
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time


## 🚀 Deployment

### Docker

```bash
# Build the image
docker build -t fastapi-boilerplate .

# Run the container
docker run -p 8000:8000 fastapi-boilerplate
```

### Production

Use a production ASGI server like Gunicorn:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👨‍💻 Author

**Dhruv** - [Your GitHub](https://github.com/Dhruvpatel1804)

---

⭐ If you found this project helpful, please give it a star!