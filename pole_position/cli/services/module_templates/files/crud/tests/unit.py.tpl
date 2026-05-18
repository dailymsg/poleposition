from unittest.mock import Mock

import pytest

from {{package_name}}.domain.exceptions import NotFoundError
from {{package_name}}.modules.{{module_name}}.schemas import {{class_name}}Update
from {{package_name}}.modules.{{module_name}}.services import {{class_name}}CrudService


def test_get_{{module_name}}_raises_when_missing() -> None:
    service = {{class_name}}CrudService(db=Mock())
    service.repository = Mock()
    service.repository.get.return_value = None

    with pytest.raises(NotFoundError):
        service.get_{{module_name}}(123)


def test_update_{{module_name}}_delegates_to_repository() -> None:
    item = object()
    service = {{class_name}}CrudService(db=Mock())
    service.repository = Mock()
    service.repository.get.return_value = item
    service.repository.update.return_value = item

    result = service.update_{{module_name}}(
        123,
        {{class_name}}Update(name="Updated {{class_name}}"),
    )

    assert result is item
    service.repository.update.assert_called_once_with(item, name="Updated {{class_name}}")
