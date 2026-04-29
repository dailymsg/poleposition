from pathlib import Path

from pole_position.cli.services.project_locator import find_package_root, find_project_root

ROUTER_IMPORTS_MARKER = "# polepos:router-imports"
ROUTER_INCLUDES_MARKER = "# polepos:router-includes"
MODEL_IMPORTS_MARKER = "    # polepos:model-imports"
MODULE_EXPORTS_MARKER = "    # polepos:module-exports"


def add_module(module_name: str, cwd: Path | None = None) -> None:
    project_root = find_project_root(cwd)
    package_root = find_package_root(cwd)
    package_name = package_root.name
    modules_root = package_root / "modules"
    module_root = modules_root / module_name

    if module_root.exists():
        raise RuntimeError(f"Module already exists: {module_name}")

    _write_module_files(module_root, package_name, module_name)
    _write_module_tests(project_root / "tests", package_name, module_name)
    _update_modules_init(modules_root / "__init__.py", module_name)
    _update_api_router(package_root / "api" / "router.py", package_name, module_name)
    _update_db_models(package_root / "db" / "models.py", package_name, module_name)


def _write_module_files(module_root: Path, package_name: str, module_name: str) -> None:
    module_root.mkdir(parents=True)
    class_name = _to_class_name(module_name)

    files = {
        "__init__.py": _module_init_content(),
        "model.py": _model_content(package_name, module_name, class_name),
        "repository.py": _repository_content(package_name, module_name, class_name),
        "schemas.py": _schemas_content(package_name, module_name, class_name),
        "service.py": _service_content(package_name, module_name, class_name),
        "router.py": _router_content(package_name, module_name, class_name),
    }

    for file_name, content in files.items():
        (module_root / file_name).write_text(content, encoding="utf-8")


def _write_module_tests(tests_root: Path, package_name: str, module_name: str) -> None:
    class_name = _to_class_name(module_name)
    integration_root = tests_root / "integration"
    unit_root = tests_root / "unit"
    integration_root.mkdir(parents=True, exist_ok=True)
    unit_root.mkdir(parents=True, exist_ok=True)

    integration_test = integration_root / f"test_{module_name}.py"
    unit_test = unit_root / f"test_{module_name}_service.py"

    integration_test.write_text(
        _integration_test_content(module_name, class_name),
        encoding="utf-8",
    )
    unit_test.write_text(
        _unit_test_content(package_name, module_name, class_name),
        encoding="utf-8",
    )


def _update_modules_init(path: Path, module_name: str) -> None:
    export_line = f'    "{module_name}",'
    _insert_sorted_line_before_marker(
        path=path,
        line=export_line,
        marker=MODULE_EXPORTS_MARKER,
        match_prefix='    "',
    )


def _update_api_router(path: Path, package_name: str, module_name: str) -> None:
    import_line = (
        f"from {package_name}.modules.{module_name}.router import router as {module_name}_router"
    )
    include_line = (
        f'api_router.include_router({module_name}_router, prefix="/{module_name}", '
        f'tags=["{module_name}"])'
    )

    _insert_sorted_line_before_marker(
        path=path,
        line=import_line,
        marker=ROUTER_IMPORTS_MARKER,
        match_prefix="from ",
    )
    _insert_line_before_marker(
        path=path,
        line=include_line,
        marker=ROUTER_INCLUDES_MARKER,
    )


def _update_db_models(path: Path, package_name: str, module_name: str) -> None:
    import_line = f"    from {package_name}.modules.{module_name} import model  # noqa: F401"
    _insert_sorted_line_before_marker(
        path=path,
        line=import_line,
        marker=MODEL_IMPORTS_MARKER,
        match_prefix="    from ",
    )


def _module_init_content() -> str:
    return '''__all__ = [
    "model",
    "repository",
    "router",
    "schemas",
    "service",
]
'''


def _model_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from {package_name}.db.base import Base


class {class_name}(Base):
    __tablename__ = "{module_name}"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
'''


def _repository_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from sqlalchemy import select
from sqlalchemy.orm import Session

from {package_name}.modules.{module_name}.model import {class_name}


class {class_name}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[{class_name}]:
        statement = select({class_name}).order_by({class_name}.id.asc())
        return list(self.db.scalars(statement))

    def create(self, *, name: str) -> {class_name}:
        item = {class_name}(name=name)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
'''


def _schemas_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from pydantic import BaseModel, ConfigDict, Field


class {class_name}Create(BaseModel):
    name: str = Field(min_length=3, max_length=120)


class {class_name}Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
'''


def _service_content(
    package_name: str,
    module_name: str,
    class_name: str,
) -> str:
    return f'''from sqlalchemy.orm import Session

from {package_name}.bootstrap.logging import get_logger
from {package_name}.modules.{module_name}.model import {class_name}
from {package_name}.modules.{module_name}.repository import {class_name}Repository
from {package_name}.modules.{module_name}.schemas import {class_name}Create


logger = get_logger(__name__)


class {class_name}Service:
    def __init__(self, db: Session) -> None:
        self.repository = {class_name}Repository(db)

    def list_{module_name}(self) -> list[{class_name}]:
        logger.info("Listing {module_name}")
        return self.repository.list()

    def create_{module_name}(self, payload: {class_name}Create) -> {class_name}:
        logger.info("Creating {module_name}", extra={{"name": payload.name}})
        return self.repository.create(name=payload.name)
'''


def _router_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from {package_name}.api.deps import db_session
from {package_name}.modules.{module_name}.schemas import {class_name}Create, {class_name}Read
from {package_name}.modules.{module_name}.service import {class_name}Service


router = APIRouter()


@router.get("/", response_model=list[{class_name}Read])
def list_{module_name}(db: Session = Depends(db_session)) -> list[{class_name}Read]:
    return {class_name}Service(db).list_{module_name}()


@router.post("/", response_model={class_name}Read, status_code=status.HTTP_201_CREATED)
def create_{module_name}(payload: {class_name}Create, db: Session = Depends(db_session)) -> {class_name}Read:
    return {class_name}Service(db).create_{module_name}(payload)
'''


def _integration_test_content(module_name: str, class_name: str) -> str:
    return f'''from fastapi.testclient import TestClient


def test_create_and_list_{module_name}(client: TestClient) -> None:
    create_response = client.post("/api/v1/{module_name}/", json={{"name": "Main {class_name}"}})
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/{module_name}/")
    assert list_response.status_code == 200

    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Main {class_name}"
'''


def _unit_test_content(package_name: str, module_name: str, class_name: str) -> str:
    return f'''from unittest.mock import Mock

from {package_name}.modules.{module_name}.service import {class_name}Service


def test_list_{module_name}_delegates_to_repository() -> None:
    service = {class_name}Service(db=Mock())
    service.repository = Mock()

    service.list_{module_name}()

    service.repository.list.assert_called_once_with()
'''


def _insert_line_before_marker(path: Path, line: str, marker: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    marker_index = _find_marker_index(lines, marker, path)

    if line in lines:
        return

    lines.insert(marker_index, line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _insert_sorted_line_before_marker(
    *,
    path: Path,
    line: str,
    marker: str,
    match_prefix: str,
) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    marker_index = _find_marker_index(lines, marker, path)

    managed_lines = [existing for existing in lines[:marker_index] if existing.startswith(match_prefix)]
    if line in managed_lines:
        return

    managed_lines.append(line)
    managed_lines.sort()
    preserved_prefix = [existing for existing in lines[:marker_index] if not existing.startswith(match_prefix)]
    updated_lines = preserved_prefix + managed_lines + lines[marker_index:]
    path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _find_marker_index(lines: list[str], marker: str, path: Path) -> int:
    try:
        return lines.index(marker)
    except ValueError as exc:
        raise RuntimeError(f"Unsupported managed block layout: {path}") from exc


def _to_class_name(module_name: str) -> str:
    return "".join(part.capitalize() for part in module_name.split("_"))
