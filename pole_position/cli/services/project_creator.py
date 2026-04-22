import shutil
from pathlib import Path

from pole_position.cli.services.template_renderer import (
    build_context,
    render_project_files,
)


def create_project(project_name: str, project_path: Path) -> None:
    template_dir = Path(__file__).resolve().parents[2] / "template"

    if not template_dir.exists():
        raise RuntimeError(f"Template directory not found: {template_dir}")

    shutil.copytree(template_dir, project_path)

    _rename_source_package(project_path=project_path, project_name=project_name)

    context = build_context(project_name=project_name)
    render_project_files(project_path=project_path, context=context)

    _replace_project_name_in_pyproject(
        project_path=project_path,
        project_name=project_name,
    )


def _rename_source_package(project_path: Path, project_name: str) -> None:
    src_root = project_path / "src"
    source_package_dir = src_root / "app"
    target_package_dir = src_root / project_name

    if not source_package_dir.exists():
        raise RuntimeError(f"Template source package not found: {source_package_dir}")

    source_package_dir.rename(target_package_dir)


def _replace_project_name_in_pyproject(project_path: Path, project_name: str) -> None:
    pyproject_file = project_path / "pyproject.toml"

    if not pyproject_file.exists():
        raise RuntimeError(f"pyproject.toml not found: {pyproject_file}")

    content = pyproject_file.read_text(encoding="utf-8")
    content = content.replace('name = "app"', f'name = "{project_name}"')
    pyproject_file.write_text(content, encoding="utf-8")