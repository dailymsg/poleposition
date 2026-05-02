from pathlib import Path

from pole_position.cli.command import Command
from pole_position.cli.services.installer import install_project_dependencies
from pole_position.cli.services.project_creator import create_project
from pole_position.cli.services.project_name import (
    normalize_package_name,
    validate_project_name,
)


USAGE = "Usage: polepos start <project_name> [--install] [--no-bytecode]"


def run(args: list[str]) -> None:
    install = False
    no_bytecode = False
    filtered_args: list[str] = []

    for arg in args:
        if arg == "--install":
            install = True
        elif arg == "--no-bytecode":
            no_bytecode = True
        else:
            filtered_args.append(arg)

    if not filtered_args:
        print(USAGE)
        raise SystemExit(1)
    
    if len(filtered_args) > 1:
        print(f"Unexpected argument: {filtered_args[1]}")
        print(USAGE)
        raise SystemExit(1)

    project_name = filtered_args[0].strip()

    try:
        validate_project_name(project_name)
    except ValueError as exc:
        print(str(exc))
        print(USAGE)
        raise SystemExit(1)

    package_name = normalize_package_name(project_name)
    project_path = Path(project_name)

    if project_path.exists():
        print(f"Directory already exists: {project_name}")
        raise SystemExit(1)

    create_project(
        project_name=project_name,
        package_name=package_name,
        project_path=project_path,
        no_bytecode=no_bytecode,
    )
    print(f"Created project: {project_name}")

    if no_bytecode:
        print("Configured generated runtime and migration entrypoints without Python bytecode writes.")

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

    print("  alembic upgrade head")
    print(f"  uv run python -m {package_name}.run")


command = Command(
    name="start",
    aliases=("startproject",),
    handler=run,
    description="Start a new FastAPI project lifecycle",
)
