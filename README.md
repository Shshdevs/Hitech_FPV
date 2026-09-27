# Hitech FPV server

Minimal FastAPI scaffold for REST and WebSocket transport. Domain logic, persistence, and authentication are intentionally left as extension points.

The database layer uses `psycopg2` with a thread-safe PostgreSQL connection pool. Set `DATABASE_URL` in `.env` to a standard PostgreSQL DSN such as `postgresql://user:password@localhost:5432/hitech_fpv`. Pool bounds can be set with `DATABASE_POOL_MIN_SIZE` and `DATABASE_POOL_MAX_SIZE`. PostgreSQL must be running and reachable when the server starts.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env
uvicorn main:app --reload
```

OpenAPI docs are available at `/docs`; the infrastructure health check is `GET /api/v1/health` and the generic WebSocket endpoint is `/api/v1/ws`.

## Layout

- `main.py`: ASGI entrypoint
- `app/factory.py`: application assembly and lifespan hooks
- `app/core/`: settings, logging, and common error handling
- `app/core/database.py`: app-scoped PostgreSQL connection pool
- `app/services/`: service-layer folders for flying-robotics capabilities
- `app/repositories/`: boundary for SQL and database access
- `app/schemas/`: shared API response schema
- `app/api/`: versioned REST router and route modules
- `app/ws/`: WebSocket router and connection manager

Keep the dependency direction `API/WebSocket -> services -> repositories -> core/database`; shared schemas belong at the transport boundary. REST errors use the same response envelope as successful API calls. The WebSocket manager is scoped to one app process; add a broker adapter before broadcasting across multiple server workers.
