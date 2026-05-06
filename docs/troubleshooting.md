# Troubleshooting and FAQ

This page lists quick fixes for common PolePosition project lifecycle issues.

## `polepos` Is Not Found

Install the CLI as a tool:

```bash
uv tool install poleposition
```

Or install it in the active Python environment:

```bash
pip install poleposition
```

Then verify:

```bash
polepos version
```

## `polepos check` Says This Is Not a Project

Run the command from the generated project root or a nested directory inside the
project:

```bash
cd shop-api
polepos check
```

PolePosition detects a project by looking for the generated `src/<package>/`
shape, including `api/router.py` and `modules/`.

## `polepos check` Reports a Missing Managed Marker

Managed markers are insertion points for lifecycle commands such as
`polepos add module` and `polepos add integration ...`.

Restore the marker listed in the check output, then rerun:

```bash
polepos check
```

If your team intentionally owns that file manually, treat the failure as
documented drift from the PolePosition lifecycle contract.

## `polepos add module` Fails Before Writing Files

The command validates the project layout before it writes generated files. This
prevents a half-patched project when markers or generated test paths are
missing.

Run:

```bash
polepos check
```

Fix the reported structure issue, then retry the module command.

## Database Migrations Cannot Connect

Check `DATABASE_URL` in `.env`, then run:

```bash
polepos db upgrade
```

For local Docker PostgreSQL, start the stack before running migrations:

```bash
docker compose up --build
docker compose run --rm app uv run alembic upgrade head
```

## A New Model Is Not Included in Alembic Autogenerate

Standard modules are wired into `src/<package>/db/models.py` automatically.
If you manually create a model, import it from `import_models()` so Alembic can
discover its metadata.

Do not create tables during application startup. Keep schema changes in Alembic
migrations.

## Generated Tests Use SQLite

Generated test fixtures create SQLite tables for fast local tests. Application
startup does not create tables. Runtime schema changes should still go through
Alembic.

## CORS or Runtime Settings Do Not Change

Confirm the project has a copied `.env` file:

```bash
cp .env.example .env
```

Then update the relevant setting and restart the app:

```bash
uv run python -m <package>.run
```

## Integration Code Imports Optional Dependencies

Kafka and RabbitMQ scaffolds add their transport dependencies to
`pyproject.toml`. Run:

```bash
uv sync
```

LLM scaffolds are provider-agnostic stubs and do not add a provider SDK by
default.

