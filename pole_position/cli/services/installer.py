from pathlib import Path

from pole_position.cli.services.installer import install_project_dependencies
from pole_position.cli.services.project_creator import create_project


USAGE = "Usage: poleposition startproject <project_name> [--install]"


def run(args: list[str]) -> None:
    install = False
    filtered_args: list[str] = []

    for arg in args:
        if arg == "--install":
            install = True
        else:
            filtered_args.append(arg)

    if not filtered_args:
        print(USAGE)
        raise SystemExit(1)

    project_name = filtered_args[0].strip()

    if not project_name:
        print("Project name cannot be empty")
        print(USAGE)
        raise SystemExit(1)

    project_path = Path(project_name)

    if project_path.exists():
        print(f"Directory already exists: {project_name}")
        raise SystemExit(1)

    create_project(project_name=project_name, project_path=project_path)
    print(f"Created project: {project_name}")

    if install:
        try:
            print("Installing project dependencies with uv...")
            install_project_dependencies(project_path=project_path)
            print("Dependencies installed successfully.")
        except RuntimeError as exc:
            print(str(exc))
            raise SystemExit(1)

    print("")
    print("Next steps:")
    print(f"  cd {project_name}")
    print("  cp .env.example .env")

    if not install:
        print("  uv sync")

    print(f"  uv run fastapi dev src/{project_name}/main.py")