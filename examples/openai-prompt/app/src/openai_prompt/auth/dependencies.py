from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from openai_prompt.auth.schemas import AuthenticatedUser
from openai_prompt.auth.service import AuthService
from openai_prompt.domain.exceptions import AuthenticationError, AuthorizationError


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None:
        raise AuthenticationError("Authentication credentials were not provided.")

    if credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Unsupported authentication scheme.")

    return AuthService().authenticate_token(credentials.credentials)


def require_roles(*roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    required_roles = {role.strip() for role in roles if role.strip()}

    def dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if required_roles and required_roles.isdisjoint(current_user.roles):
            raise AuthorizationError("You do not have permission to access this resource.")
        return current_user

    return dependency
