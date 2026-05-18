# Module Templates

PolePosition module templates are starting points, not framework boundaries.
They create a consistent FastAPI module shape that you can edit for the real
domain.

## Template Summary

| Template | Command | Use when |
|---|---|---|
| `standard` | `polepos add module customers` | You need a database-backed REST module with model, repository, service, router, and tests. |
| `crud` | `polepos add module customers --template crud` | You want a fuller CRUD starting point with list, create, get, update, and delete routes. |
| `api-only` | `polepos add module webhooks --api-only` | You need routes and service code but no database model or repository. |
| `ai-prompt` | `polepos add module assistant --template ai-prompt` | You need an LLM-oriented module boundary and provider-agnostic adapter stubs. |

All templates update:

- `src/<package>/modules/__init__.py`
- `src/<package>/api/router.py`
- generated integration and unit tests
- `.poleposition.toml`

Database-backed templates also update `src/<package>/db/models.py` so Alembic
can discover generated SQLAlchemy models.

## Standard Template

```bash
polepos add module customers
```

Generated module files:

```text
src/<package>/modules/customers/
  __init__.py
  model.py
  repository.py
  router.py
  schemas.py
  services/
    __init__.py
    customers_service.py
```

Generated tests:

```text
tests/integration/test_customers.py
tests/unit/test_customers_service.py
```

The standard template gives you collection endpoints and simple persistence.
Use it when the domain is not yet fully shaped but you know the module should
own a table.

After changing `model.py`, create and review a migration:

```bash
polepos db revision -m "add customers table"
polepos db upgrade
polepos check
```

## CRUD Template

```bash
polepos add module customers --template crud
```

Generated module files are similar to `standard`, but the service and tests use
CRUD-specific names:

```text
src/<package>/modules/customers/
  model.py
  repository.py
  router.py
  schemas.py
  services/
    customers_crud_service.py

tests/integration/test_customers_crud.py
tests/unit/test_customers_crud_service.py
```

Generated routes:

```text
GET    /api/v1/customers/
POST   /api/v1/customers/
GET    /api/v1/customers/{item_id}
PATCH  /api/v1/customers/{item_id}
DELETE /api/v1/customers/{item_id}
```

Use `crud` when a team wants a more complete REST skeleton immediately. The
generated fields are intentionally simple (`id` and `name`) so you can reshape
the model, schemas, repository, and service for the real aggregate.

## API-Only Template

```bash
polepos add module webhooks --api-only
polepos add module webhooks --template api-only
```

Generated module files:

```text
src/<package>/modules/webhooks/
  __init__.py
  router.py
  schemas.py
  services/
    __init__.py
    webhooks_service.py
```

API-only modules do not create:

- `model.py`
- `repository.py`
- `db/models.py` imports
- migrations

Use this template for webhooks, health-adjacent routes, proxies, callbacks, or
other API surfaces whose state lives elsewhere.

## AI Prompt Template

```bash
polepos add module assistant --template ai-prompt
```

Generated module files:

```text
src/<package>/modules/assistant/
  __init__.py
  orchestrator.py
  prompts.py
  router.py
  schemas.py
  services/
    __init__.py
    assistant_service.py
```

When missing, the command also creates shared LLM integration stubs:

```text
src/<package>/integrations/llm/
  anthropic_client.py
  factory.py
  openai_client.py
  provider.py
  schemas.py
```

The generated LLM adapters are provider-agnostic stubs. Add real SDK calls only
after deciding which provider and deployment model the application should use.

## Choosing a Template

Choose `standard` when persistence matters but the API shape is still small.
Choose `crud` when the first useful version needs full item lifecycle routes.
Choose `api-only` when the route should not own database state. Choose
`ai-prompt` when orchestration and prompt boundaries are more important than a
database model.

Do not use generated module templates as final domain design. Treat them as a
consistent first commit, then refine names, validation, relationships,
transactions, authorization, and tests for the real use case.

## Validation

Run:

```bash
polepos check
```

`check` uses `.poleposition.toml` first, then structural detection for older
projects. If a generated module directory was removed manually, use:

```bash
polepos remove module <name>
```

to clean managed router, model, export, and test references. Use
`--wiring-only` when customized module files should be preserved while
PolePosition-managed references are detached.
