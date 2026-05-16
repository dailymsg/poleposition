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
`polepos add module`, `polepos remove module`, and
`polepos add integration ...`.

Restore the marker listed in the check output, then rerun:

```bash
polepos check
```

If your team intentionally owns that file manually, treat the failure as
documented drift from the PolePosition lifecycle contract.

## What User Changes Should I Avoid?

You can edit normal FastAPI application code freely, especially code inside a
generated module. Avoid changing the files and markers that PolePosition uses
as lifecycle insertion points unless you intend to manage that surface manually.

Do not remove or rename `# polepos:*` marker comments in:

- `src/<package>/api/router.py`
- `src/<package>/db/models.py`
- `src/<package>/modules/__init__.py`
- `src/<package>/settings.py`
- `.env.example`

Also keep `.poleposition.toml` in sync when you rename the application package,
change the intended database mode, or intentionally detach generated modules or
integrations.

Avoid manually rewriting generated router includes, model imports, module
exports, integration settings, or integration env examples into a different
shape. If you need custom behavior, add code around the managed block instead
of replacing the managed block itself.

Also avoid deleting generated module directories by hand. Prefer:

```bash
polepos remove module <name>
polepos check
```

If the directory was already deleted manually, rerun
`polepos remove module <name>` so PolePosition can clean remaining generated
wiring and tests.

If `polepos check` reports orphan module references, it means generated wiring
or tests still point at a module directory that no longer exists. This includes
custom Python imports below PolePosition markers, not only the original
generated lines. Run:

```bash
polepos remove module <name>
```

or restore the missing module directory. If the remaining line is custom code,
remove or rewire it manually. Examples of references that can keep a missing
module visible to `check`:

```python
from myapp.modules.garage.router import router as garage_custom_router
api_router.include_router(garage_custom_router, prefix="/garage-custom")
from myapp.modules.garage import model as garage_model
```

## `polepos add module` Fails Before Writing Files

The command validates the project layout before it writes generated files. This
prevents a half-patched project when markers or generated test paths are
missing.

Run:

```bash
polepos check
```

Fix the reported structure issue, then retry the module command.

## `polepos remove module` Fails Before Deleting Files

The command removes only wiring it can recognize as PolePosition-managed. If a
router include, model import, or module export has been manually reformatted or
rewritten, `remove module` stops before deleting the module directory.
It also stops when a custom reference to the same module would remain after the
generated wiring is removed.

It also stops when the module directory or generated tests appear to contain
custom changes. Run `polepos remove module <name> --trace` to see what would be
removed or updated without changing files. Use `--force` only when deleting the
customized module directory is intentional.

If you only want to clean generated wiring while preserving customized module
files, run:

```bash
polepos remove module <name> --wiring-only
```

This removes managed exports, router wiring, standard-module model imports, and
generated tests. It keeps the module directory. Move, delete, or rewire that
directory before expecting `polepos check` to pass.

Run:

```bash
polepos check
```

Then either restore the generated managed wiring shape and retry, or remove the
custom wiring manually before deleting the module.

## Integration Env Exists But `check` Says It Is Missing

`polepos check` only counts active settings and env keys. A required key in a
comment is treated as inactive:

```env
# KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

Uncomment or restore the generated active line:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

Optional generated examples may stay commented. These are examples, not
required active values:

```env
# KAFKA_COMPRESSION_TYPE=
# LLM_MAX_TOKENS=
```

The same rule applies in `settings.py`. A commented field such as
`# kafka_bootstrap_servers: str = "localhost:9092"` is not a setting and will
be reported as missing when Kafka is enabled.

## A Removed Module's Table Still Exists

`polepos remove module <name>` removes generated code and managed wiring. It
does not connect to the database, drop tables, delete rows, or create an
Alembic revision.

For a standard module with a SQLAlchemy model, removal also deletes the
generated import from `src/<package>/db/models.py`. That changes what Alembic
sees in `Base.metadata`, but the database schema remains unchanged until you
write and apply a migration:

```bash
polepos db revision -m "remove customers table"
polepos db upgrade
```

Review the generated revision before applying it. If you want to keep the table
for reporting, rollback safety, or data retention, do not apply a drop-table
migration.

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

That migration command runs inside the generated app container. Outside Docker,
use `polepos db upgrade` from the project root.

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

Generated apps read settings through a cached `get_settings()` helper. A normal
process restart is enough after editing `.env`. In tests or scripts that change
environment variables without restarting Python, clear the cache before creating
the app:

```python
from <package>.app import create_app
from <package>.settings import get_settings

get_settings.cache_clear()
app = create_app()
```

Import `create_app` from `<package>.app` for tests. The ASGI global `app` lives
in `<package>.main` for Uvicorn, and the local command remains:

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
