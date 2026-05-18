from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from {{package_name}}.db.base import Base


class User(Base):
    __tablename__ = "auth_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    roles: Mapped[str] = mapped_column(String(255), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
