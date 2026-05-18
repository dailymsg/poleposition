from sqlalchemy.orm import Session

from {{package_name}}.auth.model import User
from {{package_name}}.auth.password import hash_password, verify_password
from {{package_name}}.auth.repository import UserRepository
from {{package_name}}.auth.token import create_access_token
from {{package_name}}.auth.user_schemas import TokenResponse, UserLogin, UserRegister
from {{package_name}}.bootstrap.logging import get_logger
from {{package_name}}.domain.exceptions import AuthenticationError, DomainError


logger = get_logger(__name__)


class UserAuthService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def register(self, payload: UserRegister) -> User:
        existing = self.repository.get_by_email(payload.email)
        if existing is not None:
            raise DomainError("A user with this email already exists.")

        user = self.repository.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        logger.info("Registered auth user", extra={"user_id": user.id})
        return user

    def issue_token(self, payload: UserLogin) -> TokenResponse:
        user = self.repository.get_by_email(payload.email)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid email or password.")
        if not verify_password(payload.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")

        access_token = create_access_token(
            subject=str(user.id),
            email=user.email,
            roles=_split_roles(user.roles),
        )
        logger.info("Issued auth token", extra={"user_id": user.id})
        return TokenResponse(access_token=access_token)


def _split_roles(roles: str) -> list[str]:
    return [role.strip() for role in roles.split(",") if role.strip()]
