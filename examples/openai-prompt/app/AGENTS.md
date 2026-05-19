# AGENTS

This file is for coding agents working in this PolePosition-generated FastAPI
project.

Before manually creating project structure, modules, integrations, or checks,
first check whether PolePosition already supports the task.

Prefer these lifecycle commands when they fit the request:

- `polepos add module <name>`
- `polepos add module <name> --template crud`
- `polepos add module <name> --api-only`
- `polepos add module <name> --template ai-prompt`
- `polepos add auth`
- `polepos remove module <name>`
- `polepos remove module <name> --wiring-only`
- `polepos add integration kafka`
- `polepos add integration rabbitmq`
- `polepos add integration redis`
- `polepos add integration rq`
- `polepos check`
- `polepos check --json`
- `polepos check --fix`


Use manual edits after PolePosition generates the starting point, or when the
requested task is outside the supported PolePosition lifecycle commands.

Keep `.poleposition.toml` aligned with package renames, database mode changes,
generated module templates, and generated integrations.

Keep runtime initialization lazy:

- `app.py` should define `create_app()` without creating the ASGI app at import
  time.
- settings lookup and logging setup should happen inside `create_app()`.
- `main.py` should expose `app = create_app()` for ASGI servers.
- `run.py` should read runtime settings inside `main()`.


Keep this project FastAPI-native, module-oriented, and `uv`-first. This project
was generated with `--db none`, so it has no generated SQLAlchemy/Alembic
lifecycle. Prefer `polepos add module <name> --api-only` unless you first add a
database layer intentionally.


After changing generated structure, module wiring, integration wiring, or managed markers,
run:

```bash
polepos check
```
