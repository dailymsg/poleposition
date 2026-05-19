from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError

from rabbitmq_quick_start.auth.schemas import TokenPayload
from rabbitmq_quick_start.domain.exceptions import AuthenticationError
from rabbitmq_quick_start.settings import Settings, get_settings


def create_access_token(
    *,
    subject: str,
    email: str | None = None,
    roles: list[str] | None = None,
    expires_delta: timedelta | None = None,
    settings: Settings | None = None,
) -> str:
    resolved_settings = settings or get_settings()
    lifetime = expires_delta or timedelta(
        minutes=resolved_settings.auth_access_token_expire_minutes
    )
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "roles": roles or [],
        "iss": resolved_settings.auth_issuer,
        "iat": now,
        "exp": now + lifetime,
    }

    if email:
        payload["email"] = email

    return jwt.encode(
        payload,
        resolved_settings.auth_secret_key,
        algorithm=resolved_settings.auth_algorithm,
    )


def decode_access_token(token: str, settings: Settings | None = None) -> TokenPayload:
    resolved_settings = settings or get_settings()

    try:
        payload = jwt.decode(
            token,
            resolved_settings.auth_secret_key,
            algorithms=[resolved_settings.auth_algorithm],
            issuer=resolved_settings.auth_issuer,
        )
        return TokenPayload.model_validate(payload)
    except InvalidTokenError as exc:
        raise AuthenticationError("Invalid or expired authentication token.") from exc
    except ValidationError as exc:
        raise AuthenticationError("Authentication token payload is invalid.") from exc
