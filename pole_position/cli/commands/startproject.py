from pathlib import Path

from pole_position.cli.services.project_creator import create_project


def run(args: list[str]) -> None:
    if not args:
        print("Usage: poleposition startproject <project_name>")
        raise SystemExit(1)

    project_name = args[0].strip()

    if not project_name:
        print("Project name cannot be empty")
        raise SystemExit(1)

    project_path = Path(project_name)

    if project_path.exists():
        print(f"Directory already exists: {project_name}")
        raise SystemExit(1)

    create_project(project_name=project_name, project_path=project_path)
    print(f"Created project: {project_name}")