from collections.abc import Generator

from sqlalchemy.orm import Session

from {{project_import_name}}.auth.dependencies import get_current_user, require_roles
from {{project_import_name}}.db.session import get_db


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


__all__ = [
    "db_session",
    "get_current_user",
    "require_roles",
]
