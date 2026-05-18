from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from {{package_name}}.api.deps import db_session, get_current_user
from {{package_name}}.auth.schemas import AuthenticatedUser
from {{package_name}}.auth.user_schemas import TokenResponse, UserLogin, UserRead, UserRegister
from {{package_name}}.auth.user_service import UserAuthService


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(db_session)) -> UserRead:
    user = UserAuthService(db).register(payload)
    return UserRead(
        id=user.id,
        email=user.email,
        roles=[role.strip() for role in user.roles.split(",") if role.strip()],
        is_active=user.is_active,
    )


@router.post("/token", response_model=TokenResponse)
def issue_token(payload: UserLogin, db: Session = Depends(db_session)) -> TokenResponse:
    return UserAuthService(db).issue_token(payload)


@router.get("/me", response_model=AuthenticatedUser)
def read_current_user(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    return current_user
