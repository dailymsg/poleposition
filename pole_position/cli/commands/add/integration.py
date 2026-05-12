from pole_position.cli.command import Command
from pole_position.cli.services.integration_creator import (
    SUPPORTED_INTEGRATIONS,
    add_integration,
)
from pole_position.cli.services.project_name import normalize_package_name, validate_project_name


USAGE = "Usage: polepos add integration <integration_name>"
HELP_OPTIONS = {"-h", "--help"}


def _print_usage() -> None:
    integrations = ", ".join(SUPPORTED_INTEGRATIONS)
    print(USAGE)
    print(f"Integrations: {integrations}")


def run(args: list[str]) -> None:
    if not args:
        _print_usage()
        raise SystemExit(1)

    if len(args) == 1 and args[0] in HELP_OPTIONS:
        _print_usage()
        return

    if len(args) > 1:
        print(f"Unexpected argument: {args[1]}")
        _print_usage()
        raise SystemExit(1)

    if args[0].startswith("--"):
        print(f"Unexpected option: {args[0]}")
        _print_usage()
        raise SystemExit(1)

    raw_name = args[0].strip()
    if not raw_name:
        _print_usage()
        raise SystemExit(1)

    try:
        validate_project_name(raw_name)
        integration_name = normalize_package_name(raw_name)
        add_integration(integration_name)
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1)
    except ValueError as exc:
        print(str(exc))
        _print_usage()
        raise SystemExit(1)

    print(f"Added integration: {integration_name}")


command = Command(
    name="integration",
    handler=run,
    description="Add an external integration to the current project",
)
