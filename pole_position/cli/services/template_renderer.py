from pathlib import Path


TEXT_FILE_EXTENSIONS = {
    ".py",
    ".toml",
    ".md",
    ".env",
    ".example",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".ini",
}


def build_context(
    project_name: str,
    package_name: str,
    *,
    no_bytecode: bool = False,
) -> dict[str, str]:
    dev_run_prefix = "PYTHONDONTWRITEBYTECODE=1 " if no_bytecode else ""
    return {
        "{{project_name}}": project_name,
        "{{ package_name }}": package_name,
        "{{project_import_name}}": package_name,
        "{{ app_name }}": project_name,
        "{{dev_run_prefix}}": dev_run_prefix,
    }


def should_render_file(path: Path) -> bool:
    if path.name in {".env.example", ".gitignore"}:
        return True

    if path.suffix in TEXT_FILE_EXTENSIONS:
        return True

    return False


def render_text(content: str, context: dict[str, str]) -> str:
    rendered = content
    for key, value in context.items():
        rendered = rendered.replace(key, value)
    return rendered


def render_project_files(project_path: Path, context: dict[str, str]) -> None:
    for file_path in project_path.rglob("*"):
        if not file_path.is_file():
            continue

        if not should_render_file(file_path):
            continue

        content = file_path.read_text(encoding="utf-8")
        rendered = render_text(content, context)
        file_path.write_text(rendered, encoding="utf-8")
