from pole_position.cli.command import Command
from pole_position.cli.services.project_checker import check_project


USAGE = "Usage: polepos check"


def run(args: list[str]) -> None:
    if args:
        print(f"Unexpected argument: {args[0]}")
        print(USAGE)
        raise SystemExit(1)

    try:
        result = check_project()
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1)

    if not result.passed:
        print("PolePosition project check failed.")
        print(f"Project root: {result.project_root}")
        print(f"Package: {result.package_name}")
        print("Issues:")
        for problem in result.problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    print("PolePosition project check passed.")
    print(f"Project root: {result.project_root}")
    print(f"Package: {result.package_name}")


command = Command(
    name="check",
    handler=run,
    description="Validate the current PolePosition project",
)
