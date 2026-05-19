# HTML Swap Scenario

This guide shows a realistic PolePosition workflow for a user who wants to:

1. create a FastAPI project with PolePosition
2. generate an API-focused module with `polepos add module html --api-only`
3. accept HTML through an API endpoint
4. replace links inside that HTML
5. store swap history in PostgreSQL
6. return the updated HTML back to the caller

The goal is not classic CRUD.
The goal is a focused transformation endpoint backed by PostgreSQL:

```text
POST /api/v1/html/swap
```

This is a good example of how PolePosition can speed up project structure and
routing when the final module is not generic CRUD, but still benefits from a
real database-backed audit trail.

## Scenario Goal

Assume the user is building a backend utility API for a CMS, email platform, migration tool, or landing page pipeline.

The API does two things at once:

- it transforms incoming HTML
- it stores a record of each swap operation in PostgreSQL

That database record can later help with:

- audit logs
- debugging bad replacements
- replaying previous transformations
- reporting how many links were updated
- linking a swap request to a job, tenant, or customer

The client sends HTML like this:

```html
<html>
  <body>
    <a href="https://old.example.com/pricing">Pricing</a>
    <a href="https://old.example.com/contact">Contact</a>
  </body>
</html>
```

The API should replace matching links and return updated HTML:

```html
<html>
  <body>
    <a href="https://new.example.com/pricing">Pricing</a>
    <a href="https://new.example.com/contact">Contact</a>
  </body>
</html>
```

## Step 1: Create the Project

Start the project the usual PolePosition way:

```bash
polepos start html-tools
cd html-tools
cp .env.example .env
uv sync --extra dev
polepos db upgrade
```

Before running migrations, the user should point the project to PostgreSQL.

Example `.env` update:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/html_tools
```

If the user prefers containers, the generated Docker workflow also works well here:

```bash
docker compose up --build
docker compose run --rm app uv run alembic upgrade head
```

That Docker command runs Alembic directly inside the generated app container.
For host-based development, keep the normal `polepos db upgrade` workflow.

Then run the generated app:

```bash
uv run python -m html_tools.run
```

At this point the user already has:

- project structure
- settings management
- logging
- middleware
- database and Alembic setup
- tests
- Docker workflow

Even though this HTML use case may not need a database immediately, the user still benefits from having a consistent enterprise-ready project base.

In this PostgreSQL-backed version of the scenario, the database is part of the real business flow, not just template overhead.

## Step 2: Generate the Module

Create an API-focused module named `html`:

```bash
polepos add module html --api-only
```

PolePosition will generate:

```text
src/html_tools/modules/html/
  __init__.py
  router.py
  schemas.py
  services/
    __init__.py
    html_service.py
tests/integration/test_html.py
tests/unit/test_html_api_service.py
```

It will also update:

```text
src/html_tools/api/router.py
src/html_tools/modules/__init__.py
```

## Step 3: Decide What to Keep

For this transformation endpoint, the API-only module is the best starting
point because it skips generic CRUD and database files.

The endpoint is not primarily about:

- listing records
- creating database rows
- storing domain entities

It is primarily about:

- receiving HTML
- transforming HTML
- storing the transformation result
- keeping swap history in PostgreSQL
- returning transformed HTML

So the user should treat the generated module as a starting scaffold, then
reshape it around the real workflow.

For this scenario:

- `router.py` stays
- `schemas.py` stays
- `services/html_service.py` stays
- `model.py` is added for swap history
- `repository.py` is added for persistence

The user does not keep the generated code as-is.
Instead, they rewrite the API files and add persistence files that match the
HTML swap domain.

## Step 4: Add an HTML Parser Dependency

This scenario becomes much easier if the user parses HTML properly instead of using string replacement.

A practical option is:

```bash
uv add beautifulsoup4
```

Why this is useful:

- safer than naive string replacement
- easy to inspect `<a>` tags
- easier to extend later for `img`, `script`, `link`, and canonical URLs

## Step 5: Define the Endpoint Contract

For a clean API, use JSON input and raw HTML output.

Recommended request body:

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

Recommended response:

- content type: `text/html`
- body: updated HTML string

This keeps the endpoint focused.

If the user also wants metadata, there is a second possible design:

```json
{
  "html": "<updated html>",
  "updated_links": 1
}
```

But if the consumer expects HTML directly, raw `text/html` is the cleaner choice.

## Step 6: Rewrite `schemas.py`

The starter API schemas should be replaced with transformation-focused schemas.

Example:

```python
from pydantic import BaseModel, Field


class LinkReplacement(BaseModel):
    from_url: str = Field(min_length=1)
    to_url: str = Field(min_length=1)


class HtmlSwapRequest(BaseModel):
    html: str = Field(min_length=1)
    replacements: list[LinkReplacement] = Field(min_length=1)


class HtmlSwapResult(BaseModel):
    html: str
    updated_links: int
    swap_id: int
```

Why this shape works:

- the payload is explicit
- multiple links can be updated in one call
- the service layer stays predictable
- the API can return both transformed HTML metadata and a database record id

## Step 7: Add `model.py`

Now the module should store swap history in PostgreSQL.

A practical first model could look like this:

```python
from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from html_tools.db.base import Base


class HtmlSwap(Base):
    __tablename__ = "html_swaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_html: Mapped[str] = mapped_column(Text)
    result_html: Mapped[str] = mapped_column(Text)
    updated_links: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
```

Why this is useful:

- every swap is stored
- the team can inspect historical transformations
- the API stays stateless for clients while the backend keeps useful records

## Step 8: Add `repository.py`

The repository should save completed swap operations.

Example:

```python
from sqlalchemy.orm import Session

from html_tools.modules.html.model import HtmlSwap


class HtmlSwapRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        source_html: str,
        result_html: str,
        updated_links: int,
    ) -> HtmlSwap:
        item = HtmlSwap(
            source_html=source_html,
            result_html=result_html,
            updated_links=updated_links,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
```

## Step 9: Rewrite `services/html_service.py`

This is the core of the scenario.

The service should:

1. parse incoming HTML
2. find all `<a>` tags with `href`
3. replace matching URLs
4. store the completed swap in PostgreSQL
5. return the updated HTML result

Example implementation:

```python
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from html_tools.bootstrap.logging import get_logger
from html_tools.modules.html.repository import HtmlSwapRepository
from html_tools.modules.html.schemas import HtmlSwapRequest, HtmlSwapResult


logger = get_logger(__name__)


class HtmlService:
    def __init__(self, db: Session) -> None:
        self.repository = HtmlSwapRepository(db)

    def swap_links(self, payload: HtmlSwapRequest) -> HtmlSwapResult:
        soup = BeautifulSoup(payload.html, "html.parser")
        mapping = {item.from_url: item.to_url for item in payload.replacements}
        updated_links = 0

        for anchor in soup.find_all("a", href=True):
            current_href = anchor["href"]
            if current_href in mapping:
                anchor["href"] = mapping[current_href]
                updated_links += 1

        logger.info(
            "Swapped HTML links",
            extra={"updated_links": updated_links},
        )
        updated_html = str(soup)
        swap = self.repository.create(
            source_html=payload.html,
            result_html=updated_html,
            updated_links=updated_links,
        )
        return HtmlSwapResult(
            html=updated_html,
            updated_links=updated_links,
            swap_id=swap.id,
        )
```

This keeps the business logic in the service layer, which matches the PolePosition structure well.

## Step 10: Rewrite `router.py`

The starter API router should become a transformation endpoint.

Example:

```python
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from html_tools.api.deps import db_session
from html_tools.modules.html.schemas import HtmlSwapRequest
from html_tools.modules.html.services import HtmlService


router = APIRouter()


@router.post("/swap", response_class=HTMLResponse)
def swap_html_links(
    payload: HtmlSwapRequest,
    db: Session = Depends(db_session),
) -> HTMLResponse:
    result = HtmlService(db).swap_links(payload)
    return HTMLResponse(content=result.html)
```

This gives the user a clear and REST-friendly endpoint:

```text
POST /api/v1/html/swap
```

Even though the client receives raw HTML, the backend still persists the swap operation in PostgreSQL.

## Step 11: Create a Migration

Because the module now uses PostgreSQL, the user should create and apply a
migration after adding `model.py`:

```bash
polepos db revision -m "create html swaps table"
polepos db upgrade
```

This step is essential because the new `model.py` is now part of the
application contract.

## Step 12: Rewrite the Integration Test

The generated API-only integration test should be replaced with an HTML
transformation test.

Example:

```python
from fastapi.testclient import TestClient


def test_swap_html_links(client: TestClient) -> None:
    payload = {
        "html": (
            "<html><body>"
            "<a href=\"https://old.example.com/pricing\">Pricing</a>"
            "</body></html>"
        ),
        "replacements": [
            {
                "from_url": "https://old.example.com/pricing",
                "to_url": "https://new.example.com/pricing",
            }
        ],
    }

    response = client.post("/api/v1/html/swap", json=payload)

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "https://new.example.com/pricing" in response.text
    assert "https://old.example.com/pricing" not in response.text
```

This verifies the real user goal instead of the generated API-only default.
If the user wants deeper coverage, they can also assert that a row was written
to the database.

## Step 13: Rewrite the Unit Test

The unit test should focus on the transformation rule itself.

Example:

```python
from types import SimpleNamespace
from unittest.mock import Mock

from html_tools.modules.html.schemas import HtmlSwapRequest, LinkReplacement
from html_tools.modules.html.services import HtmlService


def test_swap_links_replaces_matching_anchor_targets() -> None:
    service = HtmlService(Mock())
    service.repository.create.return_value = SimpleNamespace(id=1)
    payload = HtmlSwapRequest(
        html=(
            "<html><body>"
            "<a href=\"https://old.example.com/contact\">Contact</a>"
            "</body></html>"
        ),
        replacements=[
            LinkReplacement(
                from_url="https://old.example.com/contact",
                to_url="https://new.example.com/contact",
            )
        ],
    )

    result = service.swap_links(payload)

    assert "https://new.example.com/contact" in result.html
    assert "https://old.example.com/contact" not in result.html
    assert result.updated_links == 1
    service.repository.create.assert_called_once()
```

If the user wants deeper coverage, they can also inspect the repository call
arguments and assert that `create(...)` received the transformed HTML.

## Step 14: Run the Module

Once the module is rewritten, the user can run:

```bash
uv run pytest
uv run python -m html_tools.run
```

Then test with a request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/html/swap \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><a href=\"https://old.example.com/pricing\">Pricing</a></body></html>",
    "replacements": [
      {
        "from_url": "https://old.example.com/pricing",
        "to_url": "https://new.example.com/pricing"
      }
    ]
  }'
```

The response body should be HTML with updated links.

## What This Scenario Shows About PolePosition

This scenario is useful because it shows what PolePosition is really good at.

PolePosition does not only help when the user wants classic CRUD.
It also helps when the user wants a specialized backend module with:

- a clear route prefix
- a place for request schemas
- a place for transformation logic
- a place for PostgreSQL-backed persistence
- predictable tests
- a scalable project layout

The generated `api-only` module is helpful here because it removes setup work
without creating generic database files that this endpoint may not need at
first:

- route registration is done
- tests are already scaffolded
- the module is already wired into the app
- there are no generic CRUD model or repository files to delete
- Alembic is still available when the scenario grows into PostgreSQL-backed
  history

The user only needs to reshape the generated module around the real business goal.

## Summary

The detailed user flow is:

1. create the project
2. add the API-only `html` module
3. point the project at PostgreSQL
4. add a model and repository for swap history
5. replace starter API schemas with transformation-focused request and result shapes
6. implement link swapping in the service layer
7. persist completed swaps in PostgreSQL
8. expose `POST /api/v1/html/swap`
9. return updated HTML directly
10. create a migration
11. rewrite tests around the real scenario

This is a strong example of using PolePosition as a structured accelerator, not just a CRUD generator.
