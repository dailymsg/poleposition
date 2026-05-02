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


STARTER_MODULES = {
    "profile",
    "races",
    "status",
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

STANDARD_MODULE_PATHS = [
    "__init__.py",
    "model.py",
    "repository.py",
    "router.py",
    "schemas.py",
    "service.py",
]

AI_PROMPT_MODULE_PATHS = [
    "__init__.py",
    "orchestrator.py",
    "prompts.py",
    "router.py",
    "schemas.py",
    "service.py",
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
    return _run_project_checks(cwd, include_lifecycle=True)


def check_core_project(cwd: Path | None = None) -> ProjectCheckResult:
    return _run_project_checks(cwd, include_lifecycle=False)


def _run_project_checks(
    cwd: Path | None = None,
    *,
    include_lifecycle: bool,
) -> ProjectCheckResult:
    project_root, package_root = _discover_core_project(cwd)
    problems: list[str] = []

    _check_project_identity(problems, project_root, package_root)
    _check_generated_structure(problems, project_root, package_root)
    _check_alembic_config(problems, project_root)
    _check_managed_markers(problems, package_root)
    if include_lifecycle:
        _check_lifecycle_wiring(problems, project_root, package_root)

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


def _check_lifecycle_wiring(
    problems: list[str],
    project_root: Path,
    package_root: Path,
) -> None:
    modules_root = package_root / "modules"
    if not modules_root.is_dir():
        return

    for module_root in sorted(modules_root.iterdir()):
        if not module_root.is_dir() or module_root.name in STARTER_MODULES:
            continue

        _check_added_module_wiring(
            problems=problems,
            project_root=project_root,
            package_root=package_root,
            module_root=module_root,
        )


def _check_added_module_wiring(
    *,
    problems: list[str],
    project_root: Path,
    package_root: Path,
    module_root: Path,
) -> None:
    module_name = module_root.name

    if not module_name.isidentifier():
        problems.append(
            f"Lifecycle module directory is not a valid Python identifier: {module_root}"
        )
        return

    module_kind = _detect_module_kind(project_root, module_root)
    required_paths = (
        AI_PROMPT_MODULE_PATHS if module_kind == "ai-prompt" else STANDARD_MODULE_PATHS
    )

    for relative_path in required_paths:
        path = module_root / relative_path
        if not path.exists():
            problems.append(
                f"Lifecycle module '{module_name}' is missing generated path: {path}"
            )

    _check_module_export(problems, package_root, module_name)
    _check_module_router_wiring(problems, package_root, module_name)
    if module_kind == "standard":
        _check_module_model_wiring(problems, package_root, module_name)
    _check_module_tests(problems, project_root, module_name, module_kind)


def _detect_module_kind(project_root: Path, module_root: Path) -> str:
    module_name = module_root.name
    ai_prompt_unit_test = (
        project_root / "tests" / "unit" / f"test_{module_name}_orchestrator.py"
    )
    standard_unit_test = (
        project_root / "tests" / "unit" / f"test_{module_name}_service.py"
    )

    if (
        (module_root / "orchestrator.py").exists()
        or (module_root / "prompts.py").exists()
        or ai_prompt_unit_test.exists()
    ):
        return "ai-prompt"

    if (
        (module_root / "model.py").exists()
        or (module_root / "repository.py").exists()
        or standard_unit_test.exists()
    ):
        return "standard"

    return "standard"


def _check_module_export(
    problems: list[str],
    package_root: Path,
    module_name: str,
) -> None:
    modules_init_path = package_root / "modules" / "__init__.py"
    lines = _read_file_lines(modules_init_path)
    if lines is None:
        return

    export_line = f'    "{module_name}",'
    if export_line not in lines:
        problems.append(
            f"Lifecycle module '{module_name}' is missing module export in "
            f"{modules_init_path}: {export_line}"
        )


def _check_module_router_wiring(
    problems: list[str],
    package_root: Path,
    module_name: str,
) -> None:
    router_path = package_root / "api" / "router.py"
    lines = _read_file_lines(router_path)
    if lines is None:
        return

    package_name = package_root.name
    import_line = (
        f"from {package_name}.modules.{module_name}.router import router as "
        f"{module_name}_router"
    )
    include_line = (
        f'api_router.include_router({module_name}_router, prefix="/{module_name}", '
        f'tags=["{module_name}"])'
    )

    if import_line not in lines:
        problems.append(
            f"Lifecycle module '{module_name}' is missing router import in "
            f"{router_path}: {import_line}"
        )

    if include_line not in lines:
        problems.append(
            f"Lifecycle module '{module_name}' is missing API router include in "
            f"{router_path}: {include_line}"
        )


def _check_module_model_wiring(
    problems: list[str],
    package_root: Path,
    module_name: str,
) -> None:
    models_path = package_root / "db" / "models.py"
    lines = _read_file_lines(models_path)
    if lines is None:
        return

    package_name = package_root.name
    import_line = (
        f"    from {package_name}.modules.{module_name} import model  # noqa: F401"
    )
    if import_line not in lines:
        problems.append(
            f"Lifecycle module '{module_name}' is missing model import in "
            f"{models_path}: {import_line}"
        )


def _check_module_tests(
    problems: list[str],
    project_root: Path,
    module_name: str,
    module_kind: str,
) -> None:
    integration_test = project_root / "tests" / "integration" / f"test_{module_name}.py"
    unit_test_name = (
        f"test_{module_name}_orchestrator.py"
        if module_kind == "ai-prompt"
        else f"test_{module_name}_service.py"
    )
    unit_test = project_root / "tests" / "unit" / unit_test_name

    if not integration_test.exists():
        problems.append(
            f"Lifecycle module '{module_name}' is missing integration test: "
            f"{integration_test}"
        )

    if not unit_test.exists():
        problems.append(
            f"Lifecycle module '{module_name}' is missing unit test: {unit_test}"
        )


def _read_file_lines(path: Path) -> list[str] | None:
    if not path.is_file():
        return None

    return path.read_text(encoding="utf-8").splitlines()
