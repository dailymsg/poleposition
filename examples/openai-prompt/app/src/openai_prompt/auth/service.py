from openai_prompt.auth.schemas import AuthenticatedUser
from openai_prompt.auth.token import decode_access_token
from openai_prompt.bootstrap.logging import get_logger


logger = get_logger(__name__)


class AuthService:
    def authenticate_token(self, token: str) -> AuthenticatedUser:
        payload = decode_access_token(token)
        logger.info("Authenticated request", extra={"subject": payload.sub})
        return AuthenticatedUser(
            subject=payload.sub,
            email=payload.email,
            roles=payload.roles,
        )
