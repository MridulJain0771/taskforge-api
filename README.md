# TaskForge API

A production-style backend service built to demonstrate the engineering patterns expected from a **Backend Engineer / SDE II**: FastAPI, PostgreSQL, Redis, JWT authentication, rate limiting, background jobs, Docker, migrations, idempotency, tests, CI, and architecture documentation.

## Why this project exists

Many portfolio APIs stop at CRUD. TaskForge adds the operational pieces that matter when an API is deployed, retried, scaled, and maintained by a team.

## Features

- FastAPI REST API with versioned routes and OpenAPI docs
- PostgreSQL + SQLAlchemy 2.0 async sessions
- Alembic database migrations
- JWT bearer authentication
- Scrypt password hashing with per-password random salts
- Redis-backed API rate limiting
- Celery background processing with retries
- Idempotent task creation using `Idempotency-Key`
- Request IDs and structured JSON logging
- Liveness and dependency-aware readiness endpoints
- Docker + Docker Compose for API, PostgreSQL, Redis, and worker
- Unit and service-backed integration tests
- GitHub Actions CI with lint, migration, and test stages

## API surface

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Create user |
| POST | `/api/v1/auth/login` | Issue JWT |
| GET | `/api/v1/users/me` | Current user |
| POST | `/api/v1/tasks` | Create task; supports `Idempotency-Key` |
| GET | `/api/v1/tasks` | Paginated task list |
| GET | `/api/v1/tasks/{id}` | Fetch task |
| PATCH | `/api/v1/tasks/{id}` | Update task |
| DELETE | `/api/v1/tasks/{id}` | Delete task |
| POST | `/api/v1/tasks/{id}/process` | Queue background processing |
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | PostgreSQL + Redis readiness probe |

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

Example:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev@example.com","password":"strong-password"}'
```

## Tests

```bash
pip install -r requirements-dev.txt
ruff check .
alembic upgrade head
pytest -q
```

Integration tests expect PostgreSQL and Redis. The GitHub Actions workflow provisions both automatically.

## Project structure

```text
app/
  api/          # HTTP routes + dependencies
  core/         # configuration, auth, middleware, logging
  db/           # SQLAlchemy engine/session/base
  models/       # persistence models
  schemas/      # Pydantic request/response contracts
  services/     # business/persistence operations
  workers/      # Celery app + background jobs
migrations/     # Alembic schema history
tests/          # unit + integration coverage
docs/           # architecture decisions
.github/         # CI workflow
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for design decisions and scaling notes.
