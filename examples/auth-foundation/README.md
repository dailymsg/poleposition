# Auth Foundation Scenario

This guide shows how to use the authentication foundation that comes with a generated PolePosition project.

It focuses on the current scope of the template:

- public endpoints
- authenticated endpoints
- role-gated endpoints
- JWT-based token verification

It does not assume a full login system yet.
This is intentional.
The current goal is to give teams a clean and reusable endpoint protection pattern from day one.

## Scenario Goal

Assume the user is building an internal API for a business application.

They want:

- `/api/v1/status` to stay public
- `/api/v1/profile/me` to require authentication
- `/api/v1/profile/admin-preview` to require an `admin` role

That is exactly the kind of boundary PolePosition's auth foundation is meant to establish.

## Step 1: Create the Project

Start the project the usual way:

```bash
polepos start secure-api
cd secure-api
cp .env.example .env
uv sync
polepos db upgrade
```

Run the app:

```bash
uv run python -m secure_api.run
```

At this point the generated project already includes:

- `src/secure_api/auth/`
- JWT token helpers
- auth dependencies
- example protected profile routes
- auth settings in `.env`

## Step 2: Review the Auth Settings

The generated `.env` contains:

```env
AUTH_SECRET_KEY=change-me-in-production
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60
AUTH_ISSUER=secure-api
```

For local development, the defaults are enough to see the flow.

Before a real deployment, the team should change at least:

- `AUTH_SECRET_KEY`
- `AUTH_ISSUER`

These settings are read from:

```text
src/secure_api/settings.py
```

## Step 3: Understand the Generated Auth Files

PolePosition adds these files:

```text
src/secure_api/auth/
  __init__.py
  dependencies.py
  schemas.py
  service.py
  token.py
```

What they do:

`token.py`
- creates and decodes JWT access tokens

`schemas.py`
- defines token payload and authenticated user shapes

`service.py`
- converts decoded token payload into an authenticated user object

`dependencies.py`
- exposes `get_current_user`
- exposes `require_roles(...)`

This separation is useful because it keeps authentication logic out of route files.

## Step 4: Understand the Generated Example Endpoints

The project includes these example routes:

```text
GET /api/v1/status
GET /api/v1/profile/me
GET /api/v1/profile/admin-preview
```

They demonstrate three distinct cases:

`/status`
- public

`/profile/me`
- requires a valid bearer token

`/profile/admin-preview`
- requires a valid bearer token
- also requires the `admin` role

This is the most important idea in the foundation:

- authentication answers: who is calling?
- authorization answers: can this user access this route?

## Step 5: Generate a Token for Local Testing

Because the current foundation does not ship with a login endpoint yet, the easiest way to test the flow is to mint a token from the generated helper.

Inside the generated project, run:

```bash
uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="user-1", email="user@example.com", roles=["member"]))'
```

This prints a JWT token.

Save it to a shell variable:

```bash
TOKEN=$(uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="user-1", email="user@example.com", roles=["member"]))')
```

For an admin token:

```bash
ADMIN_TOKEN=$(uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="admin-1", email="admin@example.com", roles=["admin","member"]))')
```

This is enough to exercise the generated protection model.

## Step 6: Test the Public Endpoint

This route should always work without authentication:

```bash
curl http://127.0.0.1:8000/api/v1/status
```

Expected result:

- status code `200`
- JSON response with app status metadata

This confirms public routes remain simple.

## Step 7: Test the Protected Endpoint Without a Token

Try the authenticated profile route without credentials:

```bash
curl http://127.0.0.1:8000/api/v1/profile/me
```

Expected result:

- status code `401`
- response like:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

This shows the endpoint boundary is protected.

## Step 8: Test the Protected Endpoint With a Valid Token

Now call the same route with the generated token:

```bash
curl http://127.0.0.1:8000/api/v1/profile/me \
  -H "Authorization: Bearer $TOKEN"
```

Expected result:

- status code `200`
- JSON body like:

```json
{
  "subject": "user-1",
  "email": "user@example.com",
  "roles": ["member"]
}
```

This confirms the generated `get_current_user` dependency works.

## Step 9: Test the Role-Gated Endpoint With a Non-Admin Token

Now call the admin-preview route with a normal member token:

```bash
curl http://127.0.0.1:8000/api/v1/profile/admin-preview \
  -H "Authorization: Bearer $TOKEN"
```

Expected result:

- status code `403`
- response like:

```json
{
  "detail": "You do not have permission to access this resource."
}
```

This is the authorization example.

The user is authenticated, but not allowed.

## Step 10: Test the Role-Gated Endpoint With an Admin Token

Now use the admin token:

```bash
curl http://127.0.0.1:8000/api/v1/profile/admin-preview \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Expected result:

- status code `200`
- JSON body including `"admin"` inside `roles`

This shows how `require_roles("admin")` is intended to be used.

## Step 11: Use the Same Pattern in New Modules

Once the user understands the built-in example, they can protect their own modules the same way.

Example:

```bash
polepos add module reports
```

Inside:

```text
src/secure_api/modules/reports/router.py
```

they can protect a route like this:

```python
from fastapi import APIRouter, Depends

from secure_api.api.deps import get_current_user, require_roles
from secure_api.auth.schemas import AuthenticatedUser


router = APIRouter()


@router.get("/mine")
def my_reports(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, str]:
    return {"owner": current_user.subject}


@router.get("/admin")
def admin_reports(
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> dict[str, str]:
    return {"scope": "admin"}
```

This keeps authentication and authorization decisions explicit at the route boundary.

## Step 12: Understand What This Foundation Does Not Do Yet

This foundation intentionally does not include:

- signup
- login endpoint
- password hashing
- refresh tokens
- database-backed user persistence
- full RBAC system

That is why this example uses `create_access_token(...)` directly for testing.

The purpose of the current foundation is narrower:

- define how protected endpoints work
- define how a current user is resolved
- define how role checks are expressed

## Step 13: Why This Is Useful

Without this foundation, every new project would need to answer the same questions again:

- where does token parsing live?
- how do we get the current user?
- what makes a route protected?
- how do we distinguish `401` and `403`?

PolePosition now answers those questions with a default pattern.

That gives the team:

- a public route example
- an authenticated route example
- an authorization example
- a consistent way to protect future endpoints

## Summary

The full user flow looks like this:

1. create a project
2. run the app
3. generate a local JWT with `create_access_token(...)`
4. call `/status` without a token
5. call `/profile/me` with and without a token
6. call `/profile/admin-preview` with a member token and an admin token
7. reuse the same auth dependencies in newly generated modules

This makes the generated auth layer practical immediately, even before a full login system exists.
