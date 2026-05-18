from sqlalchemy import select
from sqlalchemy.orm import Session

from {{package_name}}.auth.model import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return self.db.scalar(statement)

    def create(
        self,
        *,
        email: str,
        hashed_password: str,
        roles: str = "user",
    ) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            roles=roles,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
