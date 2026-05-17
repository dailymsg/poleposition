# PolePosition Architecture

This document explains how PolePosition is structured as a product and as a codebase.

For a visual overview, see the [Architecture Diagram](architecture-diagram.md).

It is meant to help both humans and coding agents answer the same questions quickly:

- what the product does
- where CLI behavior lives
- where runtime helper APIs live
- where generated project behavior lives
- how `add module` and `remove module` safely update files
- which parts are stable conventions versus evolving surfaces

## Product Shape

PolePosition is a project lifecycle CLI, not only a one-time scaffold tool or template repository.

Its value comes from connected lifecycle workflows:

1. `polepos start`
2. `polepos add module`
3. `polepos remove module`
4. `polepos add integration ...`
5. `polepos check`
6. `polepos db ...`

That means the product helps at:

- project creation
- codebase growth
- project contract checks
- schema lifecycle management

Templates are a delivery mechanism for those workflows, not the product boundary.

The generated project should stay FastAPI-native while still giving teams opinionated structure and defaults.

PolePosition also ships a small runtime helper package for application code:

```python
from polepos.data import LRUCache, Trie
```

The import package `polepos` is intentionally separate from the internal
`pole_position` implementation package. Generated applications may import
`polepos.data`; they should not import `pole_position.cli...`.

## High-Level Flow

```text
User command
  -> CLI command handler
  -> service layer
  -> template copy/render and project patching
  -> generated FastAPI project
```

More concretely:

```text
polepos start myapp
  -> startproject.py
  -> project_creator.py
  -> template_renderer.py
  -> generated app under myapp/

polepos add module users
  -> commands/add/module.py
  -> module_creator.py
  -> module_templates/
  -> generated module files + managed updates

polepos remove module users
  -> commands/remove/module.py
  -> module_remover.py
  -> removes generated module files + managed updates

polepos add integration kafka
  -> commands/add/integration.py
  -> integration_creator.py
  -> generated integration files + managed settings/dependency updates

polepos add integration rabbitmq
  -> commands/add/integration.py
  -> integration_creator.py
  -> generated integration files + managed settings/dependency updates

polepos db upgrade
  -> commands/db/upgrade.py
  -> db_runner.py
  -> Alembic in generated project

polepos check
  -> commands/check.py
  -> project_checker.py
  -> core project diagnostics + added module lifecycle wiring + opt-in integration diagnostics
```

## CLI Map

Main entry:

```text
pole_position/cli/main.py
```

Important pieces:

- `command.py`: command model
- `registry.py`: command registry
- `commands/`: user-facing command handlers
- `services/`: reusable implementation logic

Current command groups:

- `start`
- `add module`
- `remove module`
- `add integration`
- `check`
- `db upgrade`
- `db revision`
- `db downgrade`
- `help`
- `version`

## Template Map

The generated project template lives under:

```text
pole_position/template/
```

This folder is copied first, then rendered with placeholder replacement.

Main placeholders include:

- `{{project_name}}`
- `{{project_import_name}}`
- `{{no_bytecode_command_prefix}}`
- `{{no_bytecode_readme_note}}`

Rendering logic lives in:

```text
pole_position/cli/services/template_renderer.py
```

## Generated Project Shape

Generated apps use this layout:

```text
src/<package>/
  app.py
  main.py
  run.py
  settings.py
  auth/
  bootstrap/
  api/
  db/
  domain/
  integrations/
  modules/
```

The responsibilities are:

- `app.py`: FastAPI application factory; it reads settings and configures
  logging when `create_app()` is called
- `main.py`: ASGI import target; it exposes `app = create_app()` for Uvicorn
- `run.py`: local/runtime process entrypoint; it prints startup details and
  starts Uvicorn from settings
- `auth/`: endpoint authentication foundation
- `bootstrap/`: logging, middleware, lifespan, error wiring
- `api/`: API composition and shared dependencies
- `db/`: SQLAlchemy base, session, model import aggregation
- `domain/`: domain exceptions and shared primitives
- `integrations/`: external systems such as LLM adapters
- `modules/`: feature modules such as `status`, `users`, `customers`

## Runtime Entrypoints

Generated apps separate application construction from process startup:

```text
app.py
  -> create_app()
  -> read settings
  -> setup logging
  -> build FastAPI app

main.py
  -> app = create_app()
  -> ASGI import target for Uvicorn

run.py
  -> main()
  -> read settings
  -> print startup table
  -> uvicorn.run("<package>.main:app", ...)
```

This separation is deliberate. Importing `src/<package>/app.py` should not
freeze `.env` values or configure logging by itself. Tests and dynamic runtime
overrides can import `create_app`, update environment values, clear the
`get_settings()` cache when needed, and then call `create_app()`.

## `add module` Architecture

`polepos add module` has two layers:

1. template selection
2. project patching

Template selection lives in:

```text
pole_position/cli/services/module_templates/
```

Current templates:

- `standard`
- `ai-prompt`
- `api-only`

Project patching lives in:

```text
pole_position/cli/services/module_creator.py
```

This file:

- writes module files
- writes generated tests
- updates shared registration points
- optionally adds LLM integration files
- optionally patches settings and `.env.example`

Module routers use local paths. A generated standard module can define
`@router.get("/")` and `@router.post("/")` inside
`src/<package>/modules/<name>/router.py`; `module_creator.py` then registers the
router once in `src/<package>/api/router.py` with `prefix="/<name>"`. The
FastAPI app applies the app-level API prefix in `app.py`, so a `customers`
module root route is served as `/api/v1/customers/`, not as a shared global `/`.

The `--api-only` CLI option is a shortcut for the `api-only` template. It
generates router, schemas, a module-local `services/` package, and tests
without model, repository, or database model wiring.

## `remove module` Architecture

`polepos remove module` is the cleanup counterpart to `add module`.

Implementation lives in:

```text
pole_position/cli/services/module_remover.py
```

The remover detects the generated module template, then removes:

- `src/<package>/modules/<name>/`
- generated integration and unit tests for the detected template
- the module export from `modules/__init__.py`
- the API router import and include from `api/router.py`
- the model import from `db/models.py` for standard modules

It is a project-file operation, not a database operation. It does not open a
database connection, create a migration, drop tables, delete data, or rewrite
historical Alembic revisions. For database-backed modules, removing the model
import narrows Alembic metadata discovery; a later reviewed migration decides
whether the physical table is dropped, retained, or replaced.

For `ai-prompt` modules, removing the last AI prompt module also removes shared
LLM settings, `.env.example` values, and the `integrations/llm` scaffold. If
another AI prompt module remains, shared LLM files and settings stay in place.

The command checks managed markers, generated wiring, and generated module
content before deleting the module directory. If router, model, or export wiring
has drifted into an unsupported custom layout, it stops before removing files so
the project is not left partially cleaned. If module files or generated tests
appear to contain custom changes, it also stops unless `--force` is used.
`--trace` reports the planned removals and updates without mutating files.

Router and model wiring checks are Python-aware. The remover can delete the
generated `from <package>.modules.<name>.router ...` import and matching
`api_router.include_router(...)` call, including multi-line generated calls. It
does not delete additional custom imports or includes for the same module. Those
custom references block removal until the user removes or rewires them.

`--wiring-only` is the escape hatch for customized module directories. It
removes PolePosition-managed exports, router wiring, standard-module model
imports, and generated tests, but preserves the module directory and shared
integration scaffolds. This lets users detach generated wiring without deleting
custom code.

## `add integration` Architecture

`polepos add integration ...` grows an existing project with external system
helpers while keeping the base template lean.

Current integrations:

- `kafka`
- `rabbitmq`

Messaging support is intentionally opt-in. Kafka writes `integrations/kafka`
helpers and adds `aiokafka`; RabbitMQ writes `integrations/rabbitmq` helpers
and adds `aio-pika`. Both integrations patch settings and `.env.example`
values. Consumer loops are left as explicit worker/runtime code instead of
being started inside the FastAPI app process.

Integration env handling distinguishes active required keys from optional
commented examples. A required key that appears only as a comment is treated as
missing, so `polepos add integration kafka` inserts an active
`KAFKA_BOOTSTRAP_SERVERS=...` line even if `# KAFKA_BOOTSTRAP_SERVERS=...`
already exists. Optional examples such as `# KAFKA_COMPRESSION_TYPE=` and
`# LLM_MAX_TOKENS=` are allowed to remain commented.

Integration dependency patching targets `[project].dependencies` in
`pyproject.toml`. It tolerates normal TOML formatting differences such as
inline or multi-line arrays, but it does not patch dependency groups or
tool-specific dependency lists.

## `check` Architecture

`polepos check` is the lifecycle contract validator. It keeps project
diagnostics separate from project mutation: it reads generated files and reports
drift, but it does not patch files, install packages, connect to databases, or
start external services.

Implementation lives in:

```text
pole_position/cli/services/project_checker.py
```

The command handler lives in:

```text
pole_position/cli/commands/check.py
```

Current check layers:

- core checks: project identity, generated structure, Alembic config, and managed markers
- lifecycle checks: added module files, exports, router wiring, model wiring, and generated tests
- integration checks: Kafka, RabbitMQ, and LLM files, dependencies, settings keys, and env keys

Lifecycle orphan checks parse router and model Python files across the whole
file, not just lines before managed markers. This lets `check` report custom
imports that still reference a missing module after the generated block was
cleaned. Integration checks parse exact active setting/env keys so comments and
substring matches do not hide missing required values.

Core-only behavior is available through `check_core_project()` for internal
callers that need the foundation without lifecycle or integration checks.
The public `check_project()` path runs the full current contract.

New generated projects include `.poleposition.toml` at the project root. It is
small lifecycle metadata, not application configuration:

- application package name
- database mode: `sqlite`, `postgres`, `none`, or user-managed `custom`
- generated module templates
- generated integration scaffolds

When the manifest is present, package detection, module template detection, and
integration checks prefer it over inference. Older generated projects without
the manifest continue to use structural inference.

For the detailed user guide and agent-facing contract, see:

```text
docs/project-checks.md
```

## Managed Block Contract

`add module` and `remove module` depend on marker comments in generated files.

Current managed markers include:

- `# polepos:router-imports`
- `# polepos:router-includes`
- `# polepos:model-imports`
- `# polepos:module-exports`
- `# polepos:auth-settings`
- `# polepos:auth-env`
- `# polepos:integration-settings`
- `# polepos:integration-env`
- `# polepos:llm-settings`
- `# polepos:llm-env`

These markers define PolePosition-managed regions.

Meaning:

- PolePosition may insert generated lines before these markers
- users may add surrounding code and comments
- users should not remove these markers unless they intend to manage those files manually

The most important managed files are:

- `src/<package>/api/router.py`
- `src/<package>/db/models.py`
- `src/<package>/modules/__init__.py`
- `src/<package>/settings.py`
- `.env.example`
- `.poleposition.toml`

If these markers are removed or rearranged incorrectly, `polepos add module`,
`polepos remove module`, or `polepos add integration ...` may fail or stop
updating the file automatically.

## Database Lifecycle

PolePosition is migration-first.

Generated projects include:

- Alembic
- SQLAlchemy
- `db/models.py` as the import aggregation point

This means:

- schema changes should go through Alembic
- app startup should not recreate schema ad hoc
- new database-backed modules must be wired into `db/models.py`

The main lifecycle is:

```text
polepos start
-> edit models
-> polepos db revision -m "..."
-> polepos db upgrade
```

The remove lifecycle keeps the same separation:

```text
polepos remove module customers
-> review whether database tables should remain
-> polepos db revision -m "remove customers table"
-> polepos db upgrade
```

If the team wants to remove only API code while retaining data, it should stop
after the remove command and avoid generating a drop-table migration.

## Authentication Boundary

Generated projects now include a JWT-based authentication foundation.

The important separation is:

- authentication: who is calling?
- authorization: what can this user access?

The generated auth package provides token helpers, `get_current_user`, and
`require_roles(...)` so newly added modules can define protected and role-gated
routes explicitly.

This is meant as a reusable route-boundary pattern, not a full identity system yet.

## Logging Boundary

Generated projects support:

- `LOG_FORMAT=text`
- `LOG_FORMAT=json`

Logging is configured centrally in:

```text
src/<package>/bootstrap/logging.py
```

The generated logging contract is:

- `get_logger(__name__)` is the preferred entrypoint
- logging setup happens from `create_app()`, not at `app.py` import time
- text logs are good for development
- JSON logs are good for production pipelines

## Examples Map

Concrete scenario guides live under:

```text
examples/
```

Current examples:

- `examples/auth-foundation/`
- `examples/html-swap/`

Use these when you want to understand how the generated project should be reshaped for a real use case instead of reading only the raw template files.

## How To Read This Repo Efficiently

If you are new to the repository, the shortest reliable reading path is:

1. `README.md`
2. `AGENTS.md`
3. this file
4. `pole_position/cli/main.py`
5. `pole_position/cli/commands/`
6. `pole_position/cli/services/`
7. `pole_position/template/`
8. `pole_position/tests/`
9. `examples/`

This order helps because it moves from product intent to command flow to generated runtime behavior.
