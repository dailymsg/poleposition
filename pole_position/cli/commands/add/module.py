from pole_position.cli.command import Command
from pole_position.cli.services.module_creator import add_module
from pole_position.cli.services.module_templates import SUPPORTED_MODULE_TEMPLATES
from pole_position.cli.services.project_name import normalize_package_name, validate_project_name


USAGE = "Usage: polepos add module <module_name> [--template <template_name>]"


def _print_usage() -> None:
    templates = ", ".join(SUPPORTED_MODULE_TEMPLATES)
    print(USAGE)
    print(f"Templates: {templates}")


def run(args: list[str]) -> None:
    if not args:
        _print_usage()
        raise SystemExit(1)

    raw_name: str | None = None
    template = "standard"
    index = 0

    while index < len(args):
        argument = args[index]

        if argument == "--template":
            if index + 1 >= len(args):
                print("Missing value for --template.")
                _print_usage()
                raise SystemExit(1)
            template = args[index + 1].strip()
            index += 2
            continue

        if argument.startswith("--template="):
            template = argument.split("=", 1)[1].strip()
            index += 1
            continue

        if argument.startswith("--"):
            print(f"Unexpected option: {argument}")
            _print_usage()
            raise SystemExit(1)

        if raw_name is None:
            raw_name = argument.strip()
            index += 1
            continue

        print(f"Unexpected argument: {argument}")
        _print_usage()
        raise SystemExit(1)

    if not raw_name:
        _print_usage()
        raise SystemExit(1)

    try:
        validate_project_name(raw_name)
        module_name = normalize_package_name(raw_name)
        add_module(module_name, template=template)
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1)
    except ValueError as exc:
        print(str(exc))
        _print_usage()
        raise SystemExit(1)

    print(f"Added module: {module_name}")


command = Command(
    name="module",
    handler=run,
    description="Add a new module to the current project",
)
