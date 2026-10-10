# Aereo Task API

## Plan and architecture

This project implements the example task-management API: users register and log in, then manage their own tasks. The stack is FastAPI, async SQLAlchemy, PostgreSQL, and JWT bearer authentication. Routes stay thin; validation lives in Pydantic schemas, persistence/query logic in services, and configuration in environment-backed settings.

```text
app/
  main.py          application, middleware, OpenAPI setup
  config.py        environment configuration
  database.py      async engine and sessions
  models.py        SQLAlchemy entities and indexes
  schemas.py       request/response validation
  security.py      bcrypt and JWT helpers
  dependencies.py  database and authenticated-user dependencies
  services.py      business and persistence operations
  routers/         auth and task endpoints
tests/             async integration tests using SQLite
```

## Endpoints

- `POST /auth/register` and `POST /auth/login`
- `GET /tasks?page=1&page_size=20&status=pending&sort=created_at`
- `POST /tasks`, `GET /tasks/{id}`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`
- `GET /health`
- Interactive Swagger UI: `http://localhost:8000/docs`

## Run locally

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite+aiosqlite:///./aereo.db"
$env:JWT_SECRET = "local-development-secret-with-at-least-32-characters"
uvicorn app.main:app --reload
```

For PostgreSQL, use `docker compose up --build` after copying `.env.example` to `.env`.

## Example requests

```powershell
curl.exe -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"password123"}'
curl.exe -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=user@example.com&password=password123"
curl.exe -X POST http://localhost:8000/tasks -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"title":"Ship API","description":"Release the first version"}'
curl.exe "http://localhost:8000/tasks?page=1&page_size=20&sort=due_date" -H "Authorization: Bearer TOKEN"
```

## Tests

```powershell
pytest
```

For a larger production deployment, use Alembic migrations and a distributed rate-limit store such as Redis instead of relying on startup table creation and the default in-memory limiter.