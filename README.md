# FastAPI Realtime Chat Backend

A scalable real-time chat application backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy (async)**, **WebSockets**, and **Docker**.

---

## Features

- JWT-based authentication
- Private and group chats
- Real-time messaging using WebSockets
- Message read status
- RESTful API + Swagger Docs
- Database migrations with Alembic
- Test coverage with `pytest`
- Seed data for local development

---

## Getting Started

### Requirements

- Python 3.11+
- Docker + Docker Compose
- Pipenv

---

### Run with Docker

```bash
# Build and start the project
docker-compose up --build
```

App will be available at [http://localhost:8000](http://localhost:8000)  
API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Environment Variables

Create a `.env` file based on this template:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=chatdb
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/chatdb
JWT_SECRET=your-secret
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
```

---

## Alembic Migrations

### Create a new migration:

```bash
alembic revision --autogenerate -m "create messages table"
```

### Apply all migrations (locally):

```bash
alembic upgrade head
```

### Or via Docker:

```bash
docker-compose run --rm web alembic upgrade head
```

---

## Run Tests

### Locally:

```bash
pytest
```

### Via Docker:

```bash
docker-compose run --rm web pytest
```

---

## Seed Database

Populate your local database with test data:

```bash
docker-compose run --rm web python scripts/seed_data.py
```

After seeding, you’ll see printed user info and created chats — useful for testing.

---

## WebSocket Connections

You can connect to two different endpoints:

### 1. Notifications (e.g. system events)

```
ws://localhost:8000/ws/notifications?token=<JWT_TOKEN>
```

### 2. Chat messages

```
ws://localhost:8000/ws/chat/{chat_id}?token=<JWT_TOKEN>
```

> Use `Authorization: Bearer <token>` to authenticate on REST endpoints.  
> Use `?token=<JWT_TOKEN>` in query string for WebSocket connections.

---

## Tech Stack

- FastAPI
- SQLAlchemy (async)
- Alembic
- PostgreSQL
- Redis (planned)
- WebSockets
- Docker & Docker Compose
- Pipenv
- Pytest

