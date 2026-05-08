from pathlib import Path

from pole_position.cli.command import Command
from pole_position.cli.services.module_remover import RemovedModuleResult
from pole_position.cli.services.module_remover import remove_module
from pole_position.cli.services.project_name import normalize_package_name
from pole_position.cli.services.project_name import validate_project_name


USAGE = "Usage: polepos remove module <module_name>"


def _print_usage() -> None:
    print(USAGE)


def run(args: list[str]) -> None:
    if not args:
        _print_usage()
        raise SystemExit(1)

    if args[0] in {"-h", "--help"}:
        _print_usage()
        return

    if len(args) > 1:
        print(f"Unexpected argument: {args[1]}")
        _print_usage()
        raise SystemExit(1)

    raw_name = args[0].strip()
    if not raw_name:
        _print_usage()
        raise SystemExit(1)

    try:
        validate_project_name(raw_name)
        module_name = normalize_package_name(raw_name)
        result = remove_module(module_name)
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1)
    except ValueError as exc:
        print(str(exc))
        _print_usage()
        raise SystemExit(1)

    _print_success(result)


def _print_success(result: RemovedModuleResult) -> None:
    print(f"Removed module: {result.module_name}")
    print(f"Template: {result.template}")

    if result.removed_paths:
        print("Removed:")
        for path in result.removed_paths:
            print(f"  {_relative_path(result, path)}")

    if result.updated_files:
        print("Updated:")
        for path in result.updated_files:
            print(f"  {_relative_path(result, path)}")

    print("Next steps:")
    for step in result.next_steps:
        print(f"  {step}")


def _relative_path(result: RemovedModuleResult, path: Path) -> str:
    return path.relative_to(result.project_root).as_posix()


command = Command(
    name="module",
    handler=run,
    description="Remove a generated module from the current project",
)
