import shutil
from pathlib import Path

from pole_position.cli.services.database_options import (
    DEFAULT_DATABASE,
    get_database_option,
)
from pole_position.cli.services.template_renderer import (
    build_context,
    render_project_files,
)


def create_project(
    project_name: str,
    package_name: str,
    project_path: Path,
    *,
    database: str = DEFAULT_DATABASE,
    no_bytecode: bool = False,
) -> None:
    template_dir = Path(__file__).resolve().parents[2] / "template"

    if not template_dir.exists():
        raise RuntimeError(f"Template directory not found: {template_dir}")

    database_option = get_database_option(database, package_name=package_name)

    shutil.copytree(
        template_dir,
        project_path,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    _rename_source_package(
        project_path=project_path,
        package_name=package_name,
    )

    context = build_context(
        project_name=project_name,
        package_name=package_name,
        database=database_option.name,
        no_bytecode=no_bytecode,
    )
    render_project_files(project_path=project_path, context=context)

    if not database_option.uses_database:
        _remove_database_scaffold(
            project_path=project_path,
            project_name=project_name,
            package_name=package_name,
        )


def _rename_source_package(project_path: Path, package_name: str) -> None:
    src_root = project_path / "src"
    source_package_dir = src_root / "app"
    target_package_dir = src_root / package_name

    if not source_package_dir.exists():
        raise RuntimeError(f"Template source package not found: {source_package_dir}")

    source_package_dir.rename(target_package_dir)


def _remove_database_scaffold(
    *,
    project_path: Path,
    project_name: str,
    package_name: str,
) -> None:
    package_root = project_path / "src" / package_name

    for path in (
        project_path / "alembic.ini",
        project_path / "migrations",
        package_root / "db",
    ):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    _remove_pyproject_database_dependencies(project_path / "pyproject.toml")
    _remove_env_database_values(project_path / ".env.example")
    _write_database_free_compose(project_path / "compose.yaml")
    _write_database_free_api_deps(package_root / "api" / "deps.py", package_name)
    _remove_settings_database_url(package_root / "settings.py")
    _remove_lifespan_model_imports(package_root / "bootstrap" / "lifespan.py")
    _remove_run_database_summary(package_root / "run.py")
    _write_database_free_test_conftest(
        project_path / "tests" / "conftest.py",
        project_name=project_name,
        package_name=package_name,
    )


def _remove_pyproject_database_dependencies(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    removed_dependencies = {
        '    "alembic>=1.13.0",',
        '    "psycopg[binary]>=3.2.0",',
        '    "sqlalchemy>=2.0.0",',
    }
    lines = [line for line in lines if line not in removed_dependencies]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _remove_env_database_values(path: Path) -> None:
    database_prefixes = (
        "DATABASE_URL=",
        "POSTGRES_DB=",
        "POSTGRES_USER=",
        "POSTGRES_PASSWORD=",
        "POSTGRES_PORT=",
    )
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not line.startswith(database_prefixes)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_database_free_compose(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "services:",
                "  app:",
                "    build:",
                "      context: .",
                "    env_file:",
                "      - .env",
                "    environment:",
                "      APP_HOST: 0.0.0.0",
                '      APP_RELOAD: "false"',
                "    ports:",
                '      - "${APP_PORT:-8000}:${APP_PORT:-8000}"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_database_free_api_deps(path: Path, package_name: str) -> None:
    path.write_text(
        f"""from {package_name}.auth.dependencies import get_current_user, require_roles


__all__ = [
    "get_current_user",
    "require_roles",
]
""",
        encoding="utf-8",
    )


def _remove_settings_database_url(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "from pydantic import Field, field_validator":
            updated.append("from pydantic import field_validator")
            index += 1
            continue
        if line == "    database_url: str = Field(":
            index += 3
            continue
        updated.append(line)
        index += 1

    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _remove_lifespan_model_imports(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [
        line for line in lines if ".db.models import import_models" not in line
    ]
    content = "\n".join(lines) + "\n"
    content = content.replace("\n    import_models()\n", "")
    path.write_text(content, encoding="utf-8")


def _remove_run_database_summary(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    content = content.replace("        database_url=settings.database_url,\n", "")
    path.write_text(content, encoding="utf-8")


def _write_database_free_test_conftest(
    path: Path,
    *,
    project_name: str,
    package_name: str,
) -> None:
    path.write_text(
        f"""import pytest
from fastapi.testclient import TestClient

from {package_name}.app import create_app
from {package_name}.settings import get_settings


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("AUTH_ISSUER", "{project_name}-test")

    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
""",
        encoding="utf-8",
    )
