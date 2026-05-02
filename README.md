# PolePosition

![PolePosition logo](https://raw.githubusercontent.com/erenertemden/poleposition/main/assets/logo/poleposition-python-logo.svg)

A project lifecycle CLI that puts teams in pole position when starting, growing, and maintaining enterprise FastAPI projects.

PolePosition helps you keep FastAPI's speed while avoiding the usual setup drag of enterprise backend work. It does more than render a project template: it gives teams commands for project creation, module growth, project validation, and migration workflows as the codebase evolves.

Start a new project lifecycle:

```bash
polepos start myapp --install
```

If you prefer not to generate Python bytecode while developing locally:

```bash
polepos start myapp --no-bytecode
```
[![PyPI version](https://img.shields.io/pypi/v/poleposition)](https://pypi.org/project/poleposition)
[![Python](https://img.shields.io/pypi/pyversions/poleposition)](https://pypi.org/project/poleposition)
[![License](https://img.shields.io/github/license/erenertem/poleposition)](https://raw.githubusercontent.com/erenertemden/poleposition/refs/heads/main/LICENSE)

---

## Example Output

```bash
$ polepos start myapp --install
Created project: myapp

Installing project dependencies with uv...
Dependencies installed successfully.

Next steps:
  cd myapp
  cp .env.example .env
  alembic upgrade head
  uv run python -m myapp.run
```

## Why PolePosition?

PolePosition is named for the same reason teams use it: to start enterprise FastAPI development from pole position and keep it there as the project grows.

FastAPI projects should start fast, clean, and predictable, then stay easy to extend when the target is a larger production system.

PolePosition provides:

* A scalable project structure
* Environment-based configuration
* Alembic-based database migrations
* Lifecycle commands for project creation, module growth, project validation, and database migrations
* Built-in logging
* JWT-based endpoint authentication foundations
* Testing setup
* Module-oriented organization for growing codebases
* A ready-to-run FastAPI application

Less boilerplate at project creation. Less lifecycle friction as the app grows.

---

## Why not just FastAPI?

FastAPI is excellent, but turning it into a team-ready backend lifecycle often involves:

* Recreating the same structure
* Setting up logging and configuration
* Defining module boundaries
* Wiring database foundations
* Organizing modules manually
* Adding new modules without drifting from conventions
* Keeping database migrations and model imports aligned

PolePosition removes that overhead with CLI workflows that create the project, grow the codebase, validate the project contract, and keep migrations first-class.

---

## Documentation Map

Use these files to understand the repo quickly:

* [Architecture](docs/architecture.md)
* [Feature Status](docs/feature-status.md)
* [Examples Index](examples/README.md)
* [Agent Guide](AGENTS.md)

---

## Installation

PolePosition follows a `uv`-first workflow for installation, dependency sync, migrations, and local development.

```bash
uv tool install poleposition
```

or

```bash
pip install poleposition
```

---

## Quick Start

```bash
polepos start myapp --install
cd myapp
cp .env.example .env
alembic upgrade head

uv run python -m myapp.run
```

Or start the generated app with Docker and PostgreSQL:

```bash
docker compose up --build
docker compose run --rm app uv run alembic upgrade head
```

Create and run migrations:

```bash
alembic upgrade head
alembic revision --autogenerate -m "add garage table"
```

Open your API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Usage

### Create a project

```bash
polepos start myapp --install
```

`--install` runs `uv sync` inside the generated project for you.
`--no-bytecode` configures the generated runner, Alembic entrypoint, and test
fixture setup to disable Python bytecode writes during common local workflows.

Project names:

* Must not be empty
* Must not contain whitespace
* May use hyphens like `my-app`
* Are normalized to a Python package name like `my_app`

### Manual setup

```bash
polepos start myapp
cd myapp

cp .env.example .env
uv sync
alembic upgrade head

uv run python -m myapp.run
```

### Add modules

```bash
polepos add module garage
polepos add module assistant --template ai-prompt
```

`standard` is the default template for REST and domain modules.
`ai-prompt` adds a provider-agnostic LLM endpoint skeleton with module-local
prompt orchestration and shared `integrations/llm` adapters.

### Database commands

```bash
polepos db upgrade
polepos db revision -m "add garage table"
polepos db downgrade -1
```

### Docker workflow

Generated projects include a `Dockerfile`, `.dockerignore`, and `compose.yaml`
so you can start the app with PostgreSQL in containers.

```bash
cp .env.example .env
docker compose up --build
docker compose run --rm app uv run alembic upgrade head
```

The compose setup uses the generated `run.py` entrypoint and overrides
`DATABASE_URL` so the app talks to the bundled PostgreSQL service. If you
already have PostgreSQL on `5432`, change `POSTGRES_PORT` in `.env` before
starting the compose stack.

### Logging

Generated projects use `get_logger(__name__)` from `bootstrap.logging` as the preferred logging entrypoint.

```python
from shop_api.bootstrap.logging import get_logger

logger = get_logger(__name__)
```

### Runtime configuration

Generated projects include `src/<package>/run.py` as the preferred local and production-friendly entrypoint.

Use:

```bash
uv run python -m shop_api.run
```

The runner is configured from `settings.py` and `.env`, including:

* `APP_HOST`
* `APP_PORT`
* `APP_RELOAD`
* `LOG_LEVEL`
* `UVICORN_WORKERS`
* `UVICORN_ACCESS_LOG`
* `UVICORN_PROXY_HEADERS`
* `UVICORN_FORWARDED_ALLOW_IPS`
* `UVICORN_SERVER_HEADER`
* `UVICORN_DATE_HEADER`
* `UVICORN_TIMEOUT_KEEP_ALIVE`
* `UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN`
* `UVICORN_TIMEOUT_WORKER_HEALTHCHECK`
* `UVICORN_LIMIT_CONCURRENCY`
* `UVICORN_LIMIT_MAX_REQUESTS`
* `UVICORN_LIMIT_MAX_REQUESTS_JITTER`
* `UVICORN_BACKLOG`

When the generated runner starts, it prints a compact startup table with the
current service name, environment, API prefix, database backend, host, port,
worker count, and docs URL.

### CORS

Generated projects include settings-driven CORS support with development
defaults for common localhost frontend origins.

You can control it from `.env` with:

* `CORS_ENABLED`
* `CORS_ALLOW_ORIGINS`
* `CORS_ALLOW_ORIGIN_REGEX`
* `CORS_ALLOW_CREDENTIALS`
* `CORS_ALLOW_METHODS`
* `CORS_ALLOW_HEADERS`
* `CORS_EXPOSE_HEADERS`
* `CORS_MAX_AGE`

The list-style fields accept JSON arrays in `.env`.

### Authentication

Generated projects include a minimal JWT-based authentication foundation with:

* a public `GET /api/v1/status` endpoint
* a protected `GET /api/v1/profile/me` endpoint
* a role-gated `GET /api/v1/profile/admin-preview` endpoint
* `get_current_user` and `require_roles(...)` helpers

Relevant auth settings:

* `AUTH_SECRET_KEY`
* `AUTH_ALGORITHM`
* `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES`
* `AUTH_ISSUER`

### JSON logging

Generated projects support both text and JSON logging formats.

Use:

* `LOG_FORMAT=text` for local development
* `LOG_FORMAT=json` for structured production logging

The JSON formatter includes:

* `timestamp`
* `level`
* `logger`
* `message`
* `app_name`
* `environment`
* `request_id`

### When to use which command

PolePosition is a lifecycle CLI, so the commands are meant to be used over time, not only on day one:

* `polepos start` when you want to create a new FastAPI project with the PolePosition structure
* `polepos add module` when you want to add a new REST/domain module or an AI prompt module to an existing project
* `polepos db upgrade` when you want to apply migrations to the database
* `polepos db revision -m "..."` when you changed models and need a new migration
* `polepos db downgrade` when you need to roll back a migration

### Examples

Concrete scenarios live under [examples/README.md](examples/README.md):

* auth foundation workflow
* PostgreSQL-backed HTML swap workflow

### Help and version

```bash
polepos help
polepos version
```

---

## CLI

```bash
polepos help
polepos start <name> [--install] [--no-bytecode]
polepos startproject <name> [--install] [--no-bytecode]
polepos add module <name>
polepos db upgrade [target]
polepos db revision -m "<message>"
polepos db downgrade <target>
polepos version
```

---

## Project Structure

```text
myapp/
├─ Dockerfile
├─ compose.yaml
├─ alembic.ini
├─ migrations/
│  └─ versions/
├─ pyproject.toml
├─ .dockerignore
├─ .env.example
├─ src/
│  └─ myapp/
│     ├─ run.py
│     ├─ main.py
│     ├─ app.py
│     ├─ settings.py
│     ├─ bootstrap/
│     ├─ api/
│     ├─ db/
│     ├─ domain/
│     └─ modules/
│        ├─ status/
│        └─ races/
└─ tests/
   ├─ integration/
   └─ unit/
```

---

## Status Endpoint

Check if your service is running:

```http
GET /api/v1/status
```

```json
{
  "status": "ok",
  "service": "myapp",
  "environment": "development",
  "version": "0.1.0",
  "uptime_seconds": 12,
  "timestamp": "2026-04-26T12:00:00Z"
}
```

---

## Philosophy

PolePosition is built around a few principles:

* Lifecycle-oriented: supports project creation, growth, validation, and migrations
* Minimal: no unnecessary abstractions
* Opinionated: sensible defaults
* Extensible: easy to grow into larger systems

The CLI is intentionally lightweight and avoids heavy templating engines. Templates are an implementation detail; the product surface is the project lifecycle.

---

## Roadmap

* [x] Project name validation
* [x] Enterprise FastAPI project lifecycle foundation
* [x] `polepos add module`
* [x] Alembic and database migrations
* [x] Docker support
* [x] `polepos db ...` commands
* [ ] JSON logging support
* [ ] Auth foundation
* [ ] Production-ready presets

---

## Example Workflow

Here is a concrete example for a new PostgreSQL-backed FastAPI REST API project.

Create the project and install dependencies:

```bash
uv tool install poleposition
polepos start shop-api
cd shop-api
cp .env.example .env
uv sync
```

Or use the generated Docker workflow:

```bash
docker compose up --build
docker compose run --rm app uv run alembic upgrade head
```

Point the project to PostgreSQL in `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/shop_api
```

Apply the initial migration and start the API:

```bash
polepos db upgrade
uv run python -m shop_api.run
```

Add a new REST module:

```bash
polepos add module customers
```

Extend `src/shop_api/modules/customers/model.py` and `schemas.py` for your domain, then generate and apply a migration:

```bash
polepos db revision -m "add customers table"
polepos db upgrade
```

At that point, your project has:

* FastAPI app structure
* PostgreSQL-ready SQLAlchemy setup
* Alembic migration workflow
* A generated REST module with router, schemas, service, repository, and tests

That is the core PolePosition flow: start fast, add modules as the API grows, and evolve the database schema through the CLI.

### Example: build a `users` REST API

If you want a REST API that returns users, the flow is:

Generate the module:

```bash
polepos add module users
```

Update `src/shop_api/modules/users/model.py` with user fields such as:

```python
class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(default=True)
```

Update `schemas.py` so the API returns those fields, then create and apply a migration:

```bash
polepos db revision -m "create users table"
polepos db upgrade
```

At that point, you already have the generated router shape for:

```text
GET  /api/v1/users/
POST /api/v1/users/
```

From there, you refine the generated module for your actual domain instead of starting from an empty project structure.

---

## Contributing

Contributions are welcome.
Feel free to open an issue or submit a pull request.

---

## License

MIT

[License](https://raw.githubusercontent.com/erenertemden/poleposition/refs/heads/main/LICENSE)
