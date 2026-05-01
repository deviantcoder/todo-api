## ☑️ FastAPI Todo API

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/FastAPI-0.135.2-cyan?logo=fastapi&logoColor=cyan" />
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0.48-red?logo=sqlalchemy&logoColor=white" />
    <img src="https://img.shields.io/badge/Alembic-1.18.4-cyan" />
    <img src="https://img.shields.io/badge/SQLite-dev-blue?logo=sqlite&logoColor=white" />
    <img src="https://img.shields.io/badge/PostgreSQL-18-blue?logo=postgresql&logoColor=white" />
    <img src="https://img.shields.io/badge/Redis-8-red?logo=redis&logoColor=white" />
    <img src="https://img.shields.io/badge/Celery-5.6.3-lime?logo=celery&logoColor=white" />
    <img src="https://img.shields.io/badge/RabbitMQ-4.0-orange?logo=rabbitmq&logoColor=white" />
    <img src="https://img.shields.io/badge/uv-package%20manager-red?logo=uv&logoColor=white" />
    <img src="https://img.shields.io/badge/MIT-license-green" />
</p>

---

# 🚀 Todo API

REST API for managing tasks, projects, users and memberships.

Built with modern Python tools and a clean layered architecture.

## 📦 Tech Stack

- **FastAPI** — web framework
- **Pydantic** — data validation & settings management
- **SQLAlchemy** — ORM / database access
- **Alembic** — database migrations
- **PostgreSQL** — primary database
- **Redis** — caching
- **uv** — package manager
- **Pytest** — unit & integration testing
- **Docker Compose** — local development environment

## 🔍 Features

- JWT authentication
- User management
- Projects & task management
- Membership / role-based access
- Redis caching
- Rate limiting
- Logging
- Database migrations
- Unit and integration tests

## ⚡ Getting Started

### Requirements

- Python 3.12+
- Docker + Docker Compose
- uv

### Install dependencies

```bash
uv sync
```

### Start services

```bash
docker compose up -d
```

### Run migrations

```bash
uv run alembic upgrade head
```

### Run the API

```bash
uv run uvicorn src.main:app --reload
```

## 🧪 Testing

### Run all tests

```bash
uv run pytest
```

## 📜 License

This project is licensed under the MIT License.
