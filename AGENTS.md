# AGENTS

This file is for coding agents working in this repository.

If you are an agent, read this file before making changes.
Use it as the default operating guide for understanding product intent, preferred workflows, and repo conventions.

## What PolePosition Is

PolePosition is a CLI for starting enterprise FastAPI projects from pole position.

Its purpose is not only to scaffold a new project once, but to help teams keep a consistent development flow as the project grows.

Today that flow is centered around:

- `polepos start` for creating a project
- `polepos add module` for growing the codebase
- `polepos db ...` for managing Alembic migration workflows

When in doubt, optimize for this product idea:

PolePosition should help teams keep FastAPI's speed while reducing the setup and maintenance overhead of enterprise backend work.

## Read This Before Changing Product Behavior

Prefer these product principles:

- Keep the generated project FastAPI-native.
- Prefer explicit structure over heavy framework magic.
- Prefer module-oriented organization over large flat technical layers.
- Prefer `uv`-first workflows for install, sync, run, and local developer operations.
- Prefer migration-first database workflows over startup-time schema creation.

Avoid these regressions:

- Do not reintroduce `Base.metadata.create_all()` in generated app startup code.
- Do not turn the generated project into a framework that hides FastAPI too much.
- Do not make `add module` output depend on hidden global state.
- Do not silently bypass Alembic by introducing ad hoc schema creation paths.

## Preferred User Workflow

Assume the intended user flow looks like this:

1. Create a project

```bash
polepos start shop-api
cd shop-api
cp .env.example .env
uv sync
polepos db upgrade
uv run fastapi dev src/shop_api/main.py
```

2. Add a new domain module

```bash
polepos add module customers
```

3. Refine the generated module for the real domain

- update `model.py`
- update `schemas.py`
- update `service.py`
- update `router.py` if needed

4. Create and apply a migration

```bash
polepos db revision -m "add customers table"
polepos db upgrade
```

Agents should preserve and improve this flow, not fight it.

## Generated Project Conventions

The generated app currently follows this structure:

```text
src/<package>/
  app.py
  main.py
  settings.py
  bootstrap/
  api/
  db/
  domain/
  modules/
```

Important meanings:

- `bootstrap/`: app-wide wiring such as logging, middleware, lifespan, and exception handling
- `api/`: API composition and shared dependencies
- `db/`: SQLAlchemy base, session, model import registry
- `domain/`: shared domain exceptions and similar cross-module domain primitives
- `modules/`: feature/domain modules such as `status`, `races`, `users`, `customers`

Agents should prefer adding behavior inside modules instead of creating large global folders like `services/` or `repositories/` at the project root.

## CLI Conventions

Current CLI command groups:

- `polepos start`
- `polepos add module`
- `polepos db upgrade`
- `polepos db revision -m "..."`
- `polepos db downgrade`
- `polepos help`
- `polepos version`

Design expectations:

- top-level commands should stay few and intentional
- namespace commands like `add` and `db` should scale to more subcommands over time
- usage messages should be short, direct, and actionable
- project detection should work from nested directories inside a PolePosition project

If you add new CLI behavior:

- update command registration
- update README command documentation
- add repo tests
- keep namespace structure coherent

## Database and Migration Rules

PolePosition uses:

- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

Current database philosophy:

- generated apps are migration-first
- schema changes should flow through Alembic
- `db/models.py` is the model import aggregation point for metadata discovery
- new generated modules with models should be wired into `db/models.py`

If you touch migration behavior:

- preserve `DATABASE_URL`-based configuration
- preserve `Base.metadata` as Alembic target metadata
- preserve `import_models()` in the Alembic flow
- do not move schema creation into app startup

## Module Generation Rules

`polepos add module <name>` currently generates:

- `__init__.py`
- `model.py`
- `repository.py`
- `router.py`
- `schemas.py`
- `service.py`
- integration test
- unit test

It also updates:

- `src/<package>/modules/__init__.py`
- `src/<package>/api/router.py`
- `src/<package>/db/models.py`

When changing module generation:

- keep generated code simple and readable
- keep imports sorted and deterministic
- keep generated tests useful but lightweight
- avoid generating auth-specific behavior by default
- preserve a REST-friendly starting point

Do not assume a generated module means a complete auth or domain solution.
It is a strong starting skeleton, not a full business system.

## Documentation Expectations

README is important in this repo.

If you change user-facing behavior, update README when relevant.
Especially update README if you change:

- CLI commands
- setup steps
- database workflow
- generated project structure
- example workflows

The README should help both humans and coding agents understand:

- what the product is
- which command to use when
- how a PostgreSQL + FastAPI REST workflow looks

## Testing Expectations

Repo tests are the main validation layer.

When you change behavior, prefer adding or updating tests under:

- `pole_position/tests/test_cli.py`
- `pole_position/tests/test_startproject.py`
- `pole_position/tests/test_add_module.py`
- `pole_position/tests/test_db_commands.py`

Typical validation command:

```bash
PYTHONPATH=/Users/eren/Developer/poleposition /Users/eren/.pyenv/versions/3.11.9/bin/python3 -m pytest pole_position/tests
```

If you cannot run a heavier integration flow because a dependency is missing in the environment, prefer:

- adding the highest-value repo-level test you can
- documenting what could not be executed

## Common Agent Tasks

### Add a new CLI command

1. Add a command file under the correct namespace
2. Register it in the correct root or subcommand registry
3. Add repo tests
4. Update README if user-facing

### Improve generated project template

1. Change files under `pole_position/template/`
2. Verify placeholders still render correctly
3. Update generated-project tests in `test_startproject.py`
4. Update README and template README if needed

### Change module generation

1. Update `pole_position/cli/services/module_creator.py`
2. Verify router wiring, model wiring, and test generation
3. Add or update tests under `test_add_module.py`

### Change database command behavior

1. Update files under `pole_position/cli/commands/db/`
2. Keep project-root discovery working
3. Add or update tests under `test_db_commands.py`
4. Keep README command docs aligned

## Things That Do Not Exist Yet

Do not assume these are implemented unless you add them:

- `polepos remove module`
- `polepos delete module`
- auth foundation
- Docker support
- advanced JSON logging support
- production presets

If you introduce one of these, document it clearly and add tests.

## Decision Heuristics

When several options are possible, prefer the one that:

- improves the end-to-end developer workflow
- keeps the generated app understandable to a FastAPI developer
- makes the CLI more consistent
- preserves explicit structure
- reduces manual setup for PostgreSQL-backed REST APIs

If a change would make PolePosition more magical but less understandable, prefer the more understandable version.
