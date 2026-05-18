# Auth Foundation Scenario

This guide shows how to use the authentication foundation that comes with a
generated PolePosition project.

It focuses on the current scope of the template:

- public endpoints
- authenticated endpoints
- role-gated endpoints
- JWT-based token verification

It does not assume a full login system yet. The goal is to give teams a clean
and reusable endpoint protection pattern from day one.

## Scenario Goal

Assume the user is building an internal API for a business application.

They want:

- `/api/v1/status` to stay public
- `/api/v1/account/me` to require authentication
- `/api/v1/account/admin-preview` to require an `admin` role

PolePosition provides the auth primitives. The protected routes belong in a
normal module, so this scenario creates an `account` API module and wires those
dependencies explicitly.

## Step 1: Create the Project

Start the project the usual way:

```bash
polepos start secure-api
cd secure-api
cp .env.example .env
uv sync
polepos db upgrade
```

At this point the generated project includes:

- `src/secure_api/auth/`
- JWT token helpers
- auth dependencies
- auth settings in `.env`
- a public `GET /api/v1/status` endpoint

## Step 2: Add an API Module

Create a lightweight module for account endpoints:

```bash
polepos add module account --api-only
```

PolePosition creates:

```text
src/secure_api/modules/account/
  __init__.py
  router.py
  schemas.py
  services/
    __init__.py
    account_service.py
tests/integration/test_account.py
tests/unit/test_account_api_service.py
```

The generated module is just a starting point. Replace the example account
routes with auth-focused endpoints.

## Step 3: Rewrite `router.py`

Replace:

```text
src/secure_api/modules/account/router.py
```

with:

```python
from fastapi import APIRouter, Depends

from secure_api.api.deps import get_current_user, require_roles
from secure_api.auth.schemas import AuthenticatedUser


router = APIRouter()


@router.get("/me")
def read_account(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, object]:
    return current_user.model_dump()


@router.get("/admin-preview")
def read_admin_preview(
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> dict[str, object]:
    return current_user.model_dump()
```

This demonstrates two route boundaries:

- `get_current_user` requires a valid bearer token
- `require_roles("admin")` requires a valid token with the `admin` role

## Step 4: Review the Auth Settings

The generated `.env` contains:

```env
AUTH_SECRET_KEY=change-me-in-production
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60
AUTH_ISSUER=secure-api
```

For local development, the defaults are enough to see the flow.

Before a real deployment, change at least:

- `AUTH_SECRET_KEY`
- `AUTH_ISSUER`

## Step 5: Run the App

```bash
uv run python -m secure_api.run
```

## Step 6: Generate Tokens for Local Testing

Because the current foundation does not ship with a login endpoint yet, the
easiest way to test the flow is to mint a token from the generated helper.

Inside the generated project, run:

```bash
TOKEN=$(uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="user-1", email="user@example.com", roles=["member"]))')
```

For an admin token:

```bash
ADMIN_TOKEN=$(uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="admin-1", email="admin@example.com", roles=["admin","member"]))')
```

## Step 7: Test the Public Endpoint

This route should always work without authentication:

```bash
curl http://127.0.0.1:8000/api/v1/status
```

Expected result:

- status code `200`
- JSON response with app status metadata

## Step 8: Test the Protected Endpoint Without a Token

Try the authenticated account route without credentials:

```bash
curl http://127.0.0.1:8000/api/v1/account/me
```

Expected result:

- status code `401`
- response with an authentication error

## Step 9: Test the Protected Endpoint With a Valid Token

Now call the same route with the generated token:

```bash
curl http://127.0.0.1:8000/api/v1/account/me \
  -H "Authorization: Bearer $TOKEN"
```

Expected result:

- status code `200`
- JSON body containing `subject`, `email`, and `roles`

## Step 10: Test the Role-Gated Endpoint

Call the admin-preview route with a normal member token:

```bash
curl http://127.0.0.1:8000/api/v1/account/admin-preview \
  -H "Authorization: Bearer $TOKEN"
```

Expected result:

- status code `403`
- response with an authorization error

Now use the admin token:

```bash
curl http://127.0.0.1:8000/api/v1/account/admin-preview \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Expected result:

- status code `200`
- JSON body including `"admin"` inside `roles`

## Summary

The full user flow looks like this:

1. create a project
2. add an API-only module
3. wire `get_current_user` and `require_roles(...)`
4. generate local JWTs with `create_access_token(...)`
5. call `/status` without a token
6. call `/account/me` with and without a token
7. call `/account/admin-preview` with a member token and an admin token

This makes the generated auth layer practical immediately, even before a full
login system exists.
