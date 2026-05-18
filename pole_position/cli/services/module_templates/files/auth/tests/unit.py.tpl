from unittest.mock import Mock

import pytest

from {{package_name}}.auth.user_schemas import UserRegister
from {{package_name}}.auth.user_service import UserAuthService
from {{package_name}}.domain.exceptions import DomainError


def test_register_rejects_duplicate_email() -> None:
    service = UserAuthService(db=Mock())
    service.repository = Mock()
    service.repository.get_by_email.return_value = object()

    with pytest.raises(DomainError):
        service.register(
            UserRegister(email="user@example.com", password="correct horse"),
        )
