# Configuration Reference

Generated projects use `pydantic-settings` and read values from `.env`.
Start from:

```bash
cp .env.example .env
```

Settings are resolved through `get_settings()`, which is cached for normal
runtime use. The generated FastAPI application calls `get_settings()` inside
`create_app()`, and the local runner calls it inside `run.py`'s `main()`. This
avoids import-time configuration in `app.py`.

When tests or scripts change environment variables in-process, clear the
settings cache before creating the app:

```python
from shop_api.app import create_app
from shop_api.settings import get_settings

get_settings.cache_clear()
app = create_app()
```

## Application

| Setting | Default | Purpose |
|---|---:|---|
| `APP_NAME` | project name | FastAPI title and status service name |
| `APP_ENV` | `development` | Runtime environment label |
| `APP_DEBUG` | `true` | FastAPI debug mode |
| `API_V1_PREFIX` | `/api/v1` | Prefix for the generated API router |

## Database

| Setting | Default | Purpose |
|---|---:|---|
| `DATABASE_URL` | `sqlite:///./poleposition.db` | SQLAlchemy database URL |
| `POSTGRES_DB` | `app` | Local Docker PostgreSQL database |
| `POSTGRES_USER` | `postgres` | Local Docker PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | Local Docker PostgreSQL password |
| `POSTGRES_PORT` | `5432` | Host port for local Docker PostgreSQL |

Projects generated with `polepos start --db none` omit `DATABASE_URL`,
PostgreSQL settings, SQLAlchemy, and Alembic wiring. Projects generated with
`--db postgres` start with a PostgreSQL `DATABASE_URL` instead of the SQLite
default.

Use Alembic for schema changes:

```bash
polepos db revision -m "add customers table"
polepos db upgrade
```

For the full workflow, see [Database and Migrations](database.md).

## Runtime

| Setting | Default | Purpose |
|---|---:|---|
| `APP_HOST` | `127.0.0.1` | Host passed to Uvicorn |
| `APP_PORT` | `8000` | Port passed to Uvicorn |
| `APP_RELOAD` | `true` | Uvicorn reload mode |
| `UVICORN_WORKERS` | `1` | Worker process count |
| `UVICORN_ACCESS_LOG` | `true` | Uvicorn access log toggle |
| `UVICORN_PROXY_HEADERS` | `true` | Trust proxy headers |
| `UVICORN_FORWARDED_ALLOW_IPS` | `127.0.0.1` | Allowed proxy IPs |
| `UVICORN_SERVER_HEADER` | `true` | Emit server header |
| `UVICORN_DATE_HEADER` | `true` | Emit date header |
| `UVICORN_TIMEOUT_KEEP_ALIVE` | `5` | Keep-alive timeout |
| `UVICORN_BACKLOG` | `2048` | Socket backlog |

Optional integer or boolean-like values can be left commented in `.env.example`
until needed.

`run.py` is the preferred local process entrypoint. It reads these values when
`main()` runs and starts Uvicorn with `<package>.main:app`. `main.py` exposes the
ASGI `app`, while `app.py` keeps the reusable `create_app()` factory.

## Logging

| Setting | Default | Purpose |
|---|---:|---|
| `LOG_LEVEL` | `INFO` | Python logging level |
| `LOG_FORMAT` | `text` | `text` or `json` |

Use `json` for structured production logs:

```env
LOG_FORMAT=json
```

## CORS

| Setting | Default | Purpose |
|---|---:|---|
| `CORS_ENABLED` | `true` | Enable FastAPI CORS middleware |
| `CORS_ALLOW_ORIGINS` | local frontend origins | Allowed origins |
| `CORS_ALLOW_ORIGIN_REGEX` | empty | Optional origin regex |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials |
| `CORS_ALLOW_METHODS` | common HTTP methods | Allowed methods |
| `CORS_ALLOW_HEADERS` | auth and content headers | Allowed headers |
| `CORS_EXPOSE_HEADERS` | `X-Request-ID` | Exposed response headers |
| `CORS_MAX_AGE` | `600` | Browser preflight cache seconds |

List settings accept JSON arrays:

```env
CORS_ALLOW_ORIGINS=["https://app.example.com"]
```

## Authentication

| Setting | Default | Purpose |
|---|---:|---|
| `AUTH_SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `AUTH_ALGORITHM` | `HS256` | JWT algorithm |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token lifetime |
| `AUTH_ISSUER` | project name | Expected JWT issuer |

Change `AUTH_SECRET_KEY` before deployment.

## Kafka

Kafka settings are added by:

```bash
polepos add integration kafka
```

Important values:

- `KAFKA_ENABLED`
- `KAFKA_BOOTSTRAP_SERVERS`
- `KAFKA_CLIENT_ID`
- `KAFKA_DEFAULT_TOPIC`
- `KAFKA_GROUP_ID`
- `KAFKA_REQUEST_TIMEOUT_MS`

## RabbitMQ

RabbitMQ settings are added by:

```bash
polepos add integration rabbitmq
```

Important values:

- `RABBITMQ_ENABLED`
- `RABBITMQ_URL`
- `RABBITMQ_CLIENT_ID`
- `RABBITMQ_EXCHANGE`
- `RABBITMQ_DEFAULT_ROUTING_KEY`
- `RABBITMQ_DEFAULT_QUEUE`
- `RABBITMQ_PREFETCH_COUNT`

## LLM

LLM settings are added when an AI prompt module is generated:

```bash
polepos add module assistant --template ai-prompt
```

Important values:

- `LLM_PROVIDER`
- `LLM_MODEL`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_TIMEOUT_SECONDS`
- `LLM_TEMPERATURE`
- `LLM_MAX_TOKENS`
