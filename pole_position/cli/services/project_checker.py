from dataclasses import dataclass
from pathlib import Path

from pole_position.cli.services.project_locator import find_package_root, find_project_root


MANAGED_MARKERS = {
    "api/router.py": [
        "# polepos:router-imports",
        "# polepos:router-includes",
    ],
    "db/models.py": [
        "    # polepos:model-imports",
    ],
    "modules/__init__.py": [
        "    # polepos:module-exports",
    ],
    "settings.py": [
        "    # polepos:auth-settings",
        "    # polepos:integration-settings",
        "    # polepos:llm-settings",
    ],
    "../../.env.example": [
        "# polepos:auth-env",
        "# polepos:integration-env",
        "# polepos:llm-env",
    ],
}


@dataclass(frozen=True)
class ProjectCheckResult:
    project_root: Path
    package_root: Path
    problems: list[str]

    @property
    def package_name(self) -> str:
        return self.package_root.name

    @property
    def passed(self) -> bool:
        return not self.problems


def check_project(cwd: Path | None = None) -> ProjectCheckResult:
    project_root = find_project_root(cwd)
    package_root = find_package_root(cwd)
    problems: list[str] = []

    _check_generated_structure(problems, project_root, package_root)
    _check_alembic_config(problems, project_root)
    _check_managed_markers(problems, package_root)

    return ProjectCheckResult(
        project_root=project_root,
        package_root=package_root,
        problems=problems,
    )


def _check_generated_structure(
    problems: list[str],
    project_root: Path,
    package_root: Path,
) -> None:
    required_paths = [
        project_root / "pyproject.toml",
        project_root / ".env.example",
        project_root / "README.md",
        project_root / "tests" / "conftest.py",
        package_root / "app.py",
        package_root / "main.py",
        package_root / "run.py",
        package_root / "settings.py",
        package_root / "api" / "router.py",
        package_root / "api" / "deps.py",
        package_root / "auth" / "dependencies.py",
        package_root / "auth" / "schemas.py",
        package_root / "auth" / "service.py",
        package_root / "auth" / "token.py",
        package_root / "bootstrap" / "errors.py",
        package_root / "bootstrap" / "lifespan.py",
        package_root / "bootstrap" / "logging.py",
        package_root / "bootstrap" / "middleware.py",
        package_root / "db" / "base.py",
        package_root / "db" / "models.py",
        package_root / "db" / "session.py",
        package_root / "domain" / "exceptions.py",
        package_root / "modules" / "__init__.py",
        package_root / "modules" / "races" / "router.py",
        package_root / "modules" / "status" / "router.py",
    ]

    for path in required_paths:
        if not path.exists():
            problems.append(f"Required generated path is missing: {path}")


def _check_alembic_config(problems: list[str], project_root: Path) -> None:
    required_paths = [
        project_root / "alembic.ini",
        project_root / "migrations" / "env.py",
        project_root / "migrations" / "script.py.mako",
        project_root / "migrations" / "versions",
    ]

    for path in required_paths:
        if not path.exists():
            problems.append(f"Required Alembic path is missing: {path}")


def _check_managed_markers(problems: list[str], package_root: Path) -> None:
    for relative_path, markers in MANAGED_MARKERS.items():
        path = (package_root / relative_path).resolve()

        if not path.is_file():
            problems.append(f"Managed file is missing: {path}")
            continue

        lines = path.read_text(encoding="utf-8").splitlines()
        for marker in markers:
            if marker not in lines:
                problems.append(f"Managed marker '{marker}' is missing in {path}")
