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

---

## 📦 Tech Stack

| Library | Layer |
|---|---|
| `FastAPI` | Web framework |
| `Uvicorn` | ASGI Server |
| `Pydantic` | Data validation & settings management |
| `SQLalchemy` async | ORM |
| `Alembic` | Migrations |
| `pwdlib` with argon2 + `python-jose` | Password hashing & JWT tokens |
| `aiosqlite` | SQLite driver |
| `asyncpg` | PostgreSQL driver (primary) |
| `slowapi` | Rate limiting |
| `pytest` + `pytest-asyncio` + `httpx` + `fakeredis` + `factory-boy` | Testing |
| `Redis` | Caching |
| `Celery` | Async task queue |
| `RabbitMQ` | Message broker |
| `fastapi-mail` | Email sending |
| `Docker + Docker Compose` | Containerization |
| `uv` | Package manager |

---

## 🔍 Features

- JWT authentication (access + refresh tokens)
- Email verification on signup
- Password reset via email
- User management
- Projects & task management
- Membership / role-based access
- Async email sending via Celery
- Redis caching
- Rate limiting
- Logging
- Database migrations
- Unit and integration tests

---

## API Endpoints

### Auth -- `v1/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/signup` | -- | Register a new user account |
| `POST` | `/token` | -- | Authenticate a user and issue access and refresh tokens |
| `POST` | `/refresh` | Refresh token | Rotate tokens |
| `POST` | `/logout` | Bearer | Revoke a single refresh token, logging the user out of the current session |
| `POST` | `/logout-all` | Bearer | Revoke all refresh tokens for a user, logging them out of all sessions |
| `POST` | `/change-password` | Bearer | Change the authenticated user's password |
| `POST` | `/forgot-password` | Bearer | Initiate a password reset flow for a user |
| `POST` | `/reset-password` | Bearer | Reset a user's password using a valid password reset token |
| `POST` | `/verify-email` | -- | Verify a user's email address using a verification token |
| `POST` | `/resend-verification` | -- | Resend the email verification link to a user |

### Tasks -- `v1/tasks`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Bearer | Retrieve a paginated list of tasks accessible to the user |
| `POST` | `/` | Bearer | Create a new task and assign the creating user as its owner |
| `GET` | `/<task_id>` | Bearer | Retrieve a single task by ID, enforcing view permissions |
| `PATCH` | `/<task_id>` | Bearer | Update an existing task with the provided data |
| `DELETE` | `/<task_id>` | Bearer | Delete a task by ID |

### Projects -- `v1/projects`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Bearer | Retrieve a paginated list of projects accessible to the given user |
| `POST` | `/` | Bearer | Create a new project and assign the creating user as its owner |
| `GET` | `/<project_id>` | Bearer | Retrieve a single project by ID, verifying the user has access |
| `PATCH` | `/<project_id>` | Bearer | Update an existing project, restricted to the project owner |
| `DELETE` | `/<project_id>` | Bearer | Delete a project, restricted to the project owner |

### Users -- `v1/users`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Bearer | Retrieve a paginated list of all users |
| `GET` | `/<user_id>` | Bearer | Retrieve a single user by ID |
| `GET` | `/me` | Bearer | Retrieve a current user |
| `PATCH` | `/change-username` | Bearer | Change the username of an existing user |
| `PATCH` | `/change-email` | Bearer | Change the email of an existing user |

### Membership -- `v1/projects/<project_id>/members`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Bearer | Retrieve all members of a project |
| `POST` | `/invite` | Bearer | Invite a user to a project |
| `POST` | `/accept-invite` | Bearer | Accept a pending project invitation |
| `PATCH` | `/<user_id>/update-role` | Bearer | Update the role of a project member |
| `DELETE` | `/leave` | Bearer | Remove the current user from a project |
| `DELETE` | `/<user_id>` | Bearer | Remove a member from a project |

### Search -- `v1/search`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Bearer | Search for tasks or projects |

---

## ⚡ Getting Started

### Requirements

- Python 3.14+
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

### Run the Celery worker

```bash
uv run celery -A src.worker.app worker --loglevel=info
```

### Run the Celery beat scheduler (due date reminders)

```bash
uv run celery -A src.worker.app beat --loglevel=info
```

---

## 🧪 Testing

### Run all tests

```bash
uv run pytest
```

---

## 📜 License

This project is licensed under the MIT License.

MIT © 2026
