import pytest

from pole_position.cli.services.project_name import (
    normalize_package_name,
    validate_project_name,
)


def test_normalize_package_name_with_hyphen() -> None:
    assert normalize_package_name("my-app") == "my_app"


def test_normalize_package_name_with_spaces() -> None:
    assert normalize_package_name("my app") == "my_app"


def test_validate_project_name_accepts_valid_name() -> None:
    validate_project_name("myapp")


def test_validate_project_name_accepts_hyphenated_name() -> None:
    validate_project_name("my-app")


def test_validate_project_name_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        validate_project_name("")


@pytest.mark.parametrize("name", ["foo/bar", "foo\\bar"])
def test_validate_project_name_rejects_path_separators(name: str) -> None:
    with pytest.raises(ValueError, match="path separators"):
        validate_project_name(name)


def test_validate_project_name_rejects_numeric_start() -> None:
    with pytest.raises(ValueError):
        validate_project_name("123app")


def test_validate_project_name_rejects_keyword() -> None:
    with pytest.raises(ValueError):
        validate_project_name("class")
