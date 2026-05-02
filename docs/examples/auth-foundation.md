# Auth Foundation Example

This scenario shows how to use the authentication foundation that comes with a
generated PolePosition project.

The generated project includes:

- public `GET /api/v1/status`
- protected `GET /api/v1/profile/me`
- role-gated `GET /api/v1/profile/admin-preview`
- JWT token helpers
- `get_current_user`
- `require_roles(...)`

## Create the Project

```bash
polepos start secure-api
cd secure-api
cp .env.example .env
uv sync
polepos db upgrade
uv run python -m secure_api.run
```

## Review Auth Settings

The generated `.env` contains local defaults:

```env
AUTH_SECRET_KEY=change-me-in-production
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60
AUTH_ISSUER=secure-api
```

Before deployment, change at least `AUTH_SECRET_KEY` and `AUTH_ISSUER`.

## Generate a Local Token

The foundation does not ship with a full login system yet, so local testing can
mint a token directly from the generated helper:

```bash
TOKEN=$(uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="user-1", email="user@example.com", roles=["member"]))')
```

For an admin role:

```bash
ADMIN_TOKEN=$(uv run python -c 'from secure_api.auth.token import create_access_token; print(create_access_token(subject="admin-1", email="admin@example.com", roles=["admin", "member"]))')
```

## Exercise the Boundaries

Public endpoint:

```bash
curl http://127.0.0.1:8000/api/v1/status
```

Protected endpoint:

```bash
curl http://127.0.0.1:8000/api/v1/profile/me \
  -H "Authorization: Bearer $TOKEN"
```

Admin endpoint:

```bash
curl http://127.0.0.1:8000/api/v1/profile/admin-preview \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

The important boundary is simple:

- authentication answers who is calling
- authorization answers whether that caller can access the route

Full source scenario:
[examples/auth-foundation](https://github.com/erenertemden/poleposition/blob/main/examples/auth-foundation/README.md)
