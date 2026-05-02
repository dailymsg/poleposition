# HTML Swap Example

This scenario shows how a generated module can be reshaped into a focused HTML
transformation endpoint backed by PostgreSQL history.

The target endpoint:

```text
POST /api/v1/html/swap
```

The endpoint accepts HTML, replaces configured links, stores the operation, and
returns the updated HTML.

## Create the Project

```bash
polepos start html-tools
cd html-tools
cp .env.example .env
uv sync
polepos db upgrade
uv run python -m html_tools.run
```

For PostgreSQL-backed local development, point `DATABASE_URL` at your database:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/html_tools
```

## Generate the Module

```bash
polepos add module html
```

PolePosition creates:

```text
src/html_tools/modules/html/
  __init__.py
  model.py
  repository.py
  router.py
  schemas.py
  service.py
tests/integration/test_html.py
tests/unit/test_html_service.py
```

## Reshape the Module

Keep the generated module boundary, then rewrite the internals for the real
workflow:

- `schemas.py` defines the HTML swap request contract
- `service.py` parses HTML and performs replacements
- `model.py` stores swap history
- `repository.py` persists operations
- `router.py` exposes `POST /api/v1/html/swap`

Use a parser dependency instead of string replacement:

```bash
uv add beautifulsoup4
```

## Request Shape

```json
{
  "html": "<html><body><a href=\"https://old.example.com/pricing\">Pricing</a></body></html>",
  "replacements": [
    {
      "from_url": "https://old.example.com/pricing",
      "to_url": "https://new.example.com/pricing"
    }
  ]
}
```

Return raw HTML when the consumer expects HTML directly. Return JSON only when
the caller needs metadata such as updated link count or stored operation ID.

Full source scenario:
[examples/html-swap](https://github.com/erenertemden/poleposition/blob/main/examples/html-swap/README.md)
