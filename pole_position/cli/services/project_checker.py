from dataclasses import dataclass
from pathlib import Path


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


PROJECT_IDENTITY_PATHS = [
    "pyproject.toml",
    "alembic.ini",
]

PACKAGE_IDENTITY_PATHS = [
    "app.py",
    "settings.py",
    "api",
    "bootstrap",
    "db",
    "modules",
]

CORE_PROJECT_PATHS = [
    ".env.example",
    "README.md",
    "tests/conftest.py",
]

CORE_PACKAGE_PATHS = [
    "__init__.py",
    "app.py",
    "main.py",
    "run.py",
    "settings.py",
    "api/__init__.py",
    "api/router.py",
    "api/deps.py",
    "auth/__init__.py",
    "auth/dependencies.py",
    "auth/schemas.py",
    "auth/service.py",
    "auth/token.py",
    "bootstrap/__init__.py",
    "bootstrap/errors.py",
    "bootstrap/lifespan.py",
    "bootstrap/logging.py",
    "bootstrap/middleware.py",
    "db/__init__.py",
    "db/base.py",
    "db/models.py",
    "db/session.py",
    "domain/__init__.py",
    "domain/exceptions.py",
    "modules/__init__.py",
    "modules/profile/__init__.py",
    "modules/profile/router.py",
    "modules/profile/schemas.py",
    "modules/races/__init__.py",
    "modules/races/model.py",
    "modules/races/repository.py",
    "modules/races/router.py",
    "modules/races/schemas.py",
    "modules/races/service.py",
    "modules/status/__init__.py",
    "modules/status/router.py",
    "modules/status/schemas.py",
    "modules/status/service.py",
]

ALEMBIC_PATHS = [
    "alembic.ini",
    "migrations/env.py",
    "migrations/script.py.mako",
    "migrations/versions",
]


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
    return check_core_project(cwd)


def check_core_project(cwd: Path | None = None) -> ProjectCheckResult:
    project_root, package_root = _discover_core_project(cwd)
    problems: list[str] = []

    _check_project_identity(problems, project_root, package_root)
    _check_generated_structure(problems, project_root, package_root)
    _check_alembic_config(problems, project_root)
    _check_managed_markers(problems, package_root)

    return ProjectCheckResult(
        project_root=project_root,
        package_root=package_root,
        problems=problems,
    )


def _discover_core_project(cwd: Path | None = None) -> tuple[Path, Path]:
    current = (cwd or Path.cwd()).resolve()

    for candidate in (current, *current.parents):
        package_root = _find_core_package_root_in(candidate)
        if package_root is not None:
            return candidate, package_root

    raise RuntimeError("Current directory does not look like a PolePosition project.")


def _find_core_package_root_in(project_root: Path) -> Path | None:
    src_root = project_root / "src"
    if not src_root.is_dir():
        return None

    candidates = [
        path
        for path in src_root.iterdir()
        if (
            path.is_dir()
            and path.name.isidentifier()
            and _has_core_project_signals(project_root, path)
        )
    ]

    if len(candidates) != 1:
        return None

    return candidates[0]


def _has_core_project_signals(project_root: Path, package_root: Path) -> bool:
    project_signal_count = sum(
        1
        for relative_path in PROJECT_IDENTITY_PATHS
        if (project_root / relative_path).exists()
    )
    package_signal_count = sum(
        1
        for relative_path in PACKAGE_IDENTITY_PATHS
        if (package_root / relative_path).exists()
    )

    return project_signal_count >= 1 and package_signal_count >= 2


def _check_project_identity(
    problems: list[str],
    project_root: Path,
    package_root: Path,
) -> None:
    src_root = project_root / "src"

    if not (project_root / "pyproject.toml").is_file():
        problems.append(
            f"Project identity file is missing: {project_root / 'pyproject.toml'}"
        )

    if not src_root.is_dir():
        problems.append(f"Project src directory is missing: {src_root}")

    if package_root.parent != src_root:
        problems.append(
            f"Application package is not under project src directory: {package_root}"
        )

    if not package_root.name.isidentifier():
        problems.append(
            f"Application package name is not a valid Python identifier: {package_root.name}"
        )


def _check_generated_structure(
    problems: list[str],
    project_root: Path,
    package_root: Path,
) -> None:
    required_paths = [
        *[project_root / relative_path for relative_path in CORE_PROJECT_PATHS],
        *[package_root / relative_path for relative_path in CORE_PACKAGE_PATHS],
    ]

    for path in required_paths:
        if not path.exists():
            problems.append(f"Required generated path is missing: {path}")


def _check_alembic_config(problems: list[str], project_root: Path) -> None:
    required_paths = [project_root / relative_path for relative_path in ALEMBIC_PATHS]

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
