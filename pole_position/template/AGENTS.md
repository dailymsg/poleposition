# AGENTS

This file is for coding agents working in this PolePosition-generated FastAPI
project.

Before manually creating project structure, modules, integrations, checks, or
migrations, first check whether PolePosition already supports the task.

Prefer these lifecycle commands when they fit the request:

- `polepos add module <name>`
- `polepos add module <name> --api-only`
- `polepos add module <name> --template ai-prompt`
- `polepos remove module <name>`
- `polepos add integration kafka`
- `polepos add integration rabbitmq`
- `polepos check`
- `polepos db revision -m "..."`
- `polepos db upgrade`
- `polepos db downgrade <target>`

Use manual edits after PolePosition generates the starting point, or when the
requested task is outside the supported PolePosition lifecycle commands.

Keep this project FastAPI-native, module-oriented, `uv`-first, and
migration-first. Do not add startup-time schema creation; use Alembic migrations
for database changes.

After changing generated structure, module wiring, integration wiring, managed
markers, or migration setup, run:

```bash
polepos check
```
