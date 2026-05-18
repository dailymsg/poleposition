from pole_position.cli.command import Command
from pole_position.cli.services.db_runner import run_alembic_command


USAGE = "Usage: polepos db status"


def run(args: list[str]) -> None:
    if args and args[0] in {"-h", "--help"}:
        if len(args) > 1:
            print(f"Unexpected argument: {args[1]}")
            print(USAGE)
            raise SystemExit(1)
        print(USAGE)
        return

    if args:
        print(f"Unexpected argument: {args[0]}")
        print(USAGE)
        raise SystemExit(1)

    try:
        print("Alembic current revision:")
        run_alembic_command("current", [])
        print("Alembic heads:")
        run_alembic_command("heads", [])
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1)


command = Command(
    name="status",
    handler=run,
    description="Show current and target migration revisions",
)
