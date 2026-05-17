import json

from pole_position.cli.command import Command
from pole_position.cli.services.project_checker import ProjectCheckResult
from pole_position.cli.services.project_checker import check_project


USAGE = "Usage: polepos check [--json]"
HELP_OPTIONS = {"-h", "--help"}
JSON_OPTIONS = {"--json"}


def run(args: list[str]) -> None:
    if len(args) == 1 and args[0] in HELP_OPTIONS:
        print(USAGE)
        print("Options:")
        print("  --json    Print a machine-readable JSON result.")
        return

    json_output = False
    for arg in args:
        if arg in JSON_OPTIONS:
            json_output = True
            continue
        print(f"Unexpected argument: {arg}")
        print(USAGE)
        raise SystemExit(1)

    try:
        result = check_project()
    except RuntimeError as exc:
        if json_output:
            _print_json_error(str(exc))
            raise SystemExit(1)
        print(str(exc))
        raise SystemExit(1)

    if json_output:
        _print_json_result(result)
        if not result.passed:
            raise SystemExit(1)
        return

    if not result.passed:
        print("PolePosition project check failed.")
        print(f"Project root: {result.project_root}")
        print(f"Package: {result.package_name}")
        print("Issues:")
        for issue in result.issues:
            print(f"  - [{issue.code}] {issue.message}")
            print(f"    Fix: {issue.remediation}")
        raise SystemExit(1)

    print("PolePosition project check passed.")
    print(f"Project root: {result.project_root}")
    print(f"Package: {result.package_name}")


def _print_json_result(result: ProjectCheckResult) -> None:
    payload = {
        "passed": result.passed,
        "project_root": str(result.project_root),
        "package_name": result.package_name,
        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "remediation": issue.remediation,
            }
            for issue in result.issues
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


def _print_json_error(message: str) -> None:
    payload = {
        "passed": False,
        "project_root": None,
        "package_name": None,
        "issues": [
            {
                "code": "PPCHK000",
                "message": message,
                "remediation": (
                    "Run the command from a PolePosition project root or a "
                    "nested directory inside one."
                ),
            }
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


command = Command(
    name="check",
    handler=run,
    description="Validate the current PolePosition project",
)
