from pathlib import Path

from pole_position.cli.services.project_locator import find_package_root, find_project_root
from pole_position.cli.services.module_templates import (
    SUPPORTED_MODULE_TEMPLATES,
    build_module_template,
    llm_env_block,
    llm_integration_files,
    llm_settings_block,
)

ROUTER_IMPORTS_MARKER = "# polepos:router-imports"
ROUTER_INCLUDES_MARKER = "# polepos:router-includes"
MODEL_IMPORTS_MARKER = "    # polepos:model-imports"
MODULE_EXPORTS_MARKER = "    # polepos:module-exports"
SETTINGS_LLM_MARKER = "    # polepos:llm-settings"
ENV_LLM_MARKER = "# polepos:llm-env"


def add_module(module_name: str, template: str = "standard", cwd: Path | None = None) -> None:
    if template not in SUPPORTED_MODULE_TEMPLATES:
        supported = ", ".join(SUPPORTED_MODULE_TEMPLATES)
        raise ValueError(
            f"Unsupported module template '{template}'. Expected one of: {supported}."
        )

    project_root = find_project_root(cwd)
    package_root = find_package_root(cwd)
    package_name = package_root.name
    modules_root = package_root / "modules"
    module_root = modules_root / module_name
    template_spec = build_module_template(
        template=template,
        package_name=package_name,
        module_name=module_name,
    )

    if module_root.exists():
        raise RuntimeError(f"Module already exists: {module_name}")

    _write_module_files(module_root, template_spec.files)
    _write_module_tests(project_root / "tests", template_spec)
    _update_modules_init(modules_root / "__init__.py", module_name)
    _update_api_router(package_root / "api" / "router.py", package_name, module_name)
    if template_spec.update_db_models:
        _update_db_models(package_root / "db" / "models.py", package_name, module_name)
    if template_spec.ensure_llm_integrations:
        _ensure_llm_integrations(package_root, package_name)
    if template_spec.ensure_llm_settings:
        _ensure_llm_settings(package_root / "settings.py")
        _ensure_llm_env(project_root / ".env.example")


def _write_module_files(module_root: Path, files: dict[str, str]) -> None:
    module_root.mkdir(parents=True)

    for file_name, content in files.items():
        (module_root / file_name).write_text(content, encoding="utf-8")


def _write_module_tests(tests_root: Path, template_spec) -> None:
    integration_root = tests_root / "integration"
    unit_root = tests_root / "unit"
    integration_root.mkdir(parents=True, exist_ok=True)
    unit_root.mkdir(parents=True, exist_ok=True)

    integration_test = integration_root / template_spec.integration_test_name
    unit_test = unit_root / template_spec.unit_test_name

    integration_test.write_text(
        template_spec.integration_test_content,
        encoding="utf-8",
    )
    unit_test.write_text(
        template_spec.unit_test_content,
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


def _ensure_llm_integrations(package_root: Path, package_name: str) -> None:
    for relative_path, content in llm_integration_files(package_name).items():
        path = package_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _ensure_llm_settings(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if "llm_provider:" in content:
        return

    block = llm_settings_block()
    _insert_block_before_marker_or_anchor(
        path=path,
        block=block,
        marker=SETTINGS_LLM_MARKER,
        anchor="    model_config = SettingsConfigDict(",
    )


def _ensure_llm_env(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if "LLM_PROVIDER=" in content:
        return

    block = llm_env_block()
    _insert_block_before_marker_or_anchor(
        path=path,
        block=block,
        marker=ENV_LLM_MARKER,
        anchor=None,
    )


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


def _insert_block_before_marker_or_anchor(
    *,
    path: Path,
    block: list[str],
    marker: str,
    anchor: str | None,
) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()

    if marker in lines:
        insert_at = lines.index(marker)
    elif anchor and anchor in lines:
        insert_at = lines.index(anchor)
    else:
        insert_at = len(lines)

    lines[insert_at:insert_at] = block + [""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _find_marker_index(lines: list[str], marker: str, path: Path) -> int:
    try:
        return lines.index(marker)
    except ValueError as exc:
        raise RuntimeError(f"Unsupported managed block layout: {path}") from exc
