# Auth Workflow

PolePosition generated projects include a lightweight auth foundation by
default: token helpers, current-user dependency, and role checks. The optional
`polepos add auth` command adds a database-backed registration and token
workflow on top of that foundation.

## Add Auth

```bash
polepos add auth
```

The command requires generated database wiring. Projects created with
`polepos start --db none` need an explicit database layer before using this
workflow.

Generated files:

```text
src/<package>/auth/
  model.py
  password.py
  repository.py
  router.py
  user_schemas.py
  user_service.py

tests/integration/test_auth.py
tests/unit/test_auth_service.py
```

Updated files:

- `src/<package>/api/router.py`
- `src/<package>/db/models.py`
- `pyproject.toml`
- `.poleposition.toml`

Added dependency:

```text
pwdlib[argon2]>=0.2.0
```

## Endpoints

The generated router is mounted under `/api/v1/auth`.

```text
POST /api/v1/auth/register
POST /api/v1/auth/token
GET  /api/v1/auth/me
```

Registration creates an `auth_users` row and stores a password hash. Token
login returns a JWT compatible with the generated `get_current_user`
dependency. `/me` validates the token and returns the authenticated user.

## Migration Flow

After adding auth:

```bash
uv sync --extra dev
polepos db revision -m "add auth users table"
polepos db upgrade
polepos check
```

Review the generated migration before applying it to shared environments.
Auth introduces a real table, so migration review is part of the workflow.

## Generated Model

The generated `User` model starts intentionally small:

```text
auth_users
  id
  email
  hashed_password
  roles
  is_active
```

`roles` is a comma-separated string so the first scaffold stays simple. In a
real system you may replace it with normalized role tables, permissions,
external identity provider claims, tenant-scoped membership, or policy-based
authorization.

## Security Scope

The generated auth workflow is a useful starting point, not a complete identity
product. It does not include:

- refresh tokens
- password reset
- email verification
- account lockout
- MFA
- external identity provider integration
- tenant-aware roles or permissions

Add those deliberately based on the product and threat model.

## Customization Boundaries

Safe places to customize:

- validation in `user_schemas.py`
- repository queries in `repository.py`
- registration and login policy in `user_service.py`
- response shapes and route names in `router.py`
- model fields and indexes in `model.py`

After changing model fields, create a migration. After changing route or model
wiring, run:

```bash
polepos check
```

`polepos check` validates generated auth files, tests, dependency, router
wiring, model import wiring, and database mode. If auth is intentionally
removed, detach it fully from `.poleposition.toml`, router wiring,
`db/models.py`, tests, and `pyproject.toml`.

## Using Protected Routes

Generated projects expose `get_current_user` and `require_roles` through
`api/deps.py`.

```python
from fastapi import APIRouter, Depends

from <package>.api.deps import get_current_user, require_roles
from <package>.auth.schemas import AuthenticatedUser

router = APIRouter()


@router.get("/me")
def read_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    return current_user


@router.get("/admin")
def read_admin(
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> dict[str, str]:
    return {"subject": current_user.subject}
```

Keep auth checks explicit at route boundaries. Avoid hiding authorization in
global middleware unless the entire API has the same policy.
