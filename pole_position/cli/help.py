from pole_position.cli.command import Command
from pole_position.cli.registry import registry


def run(args: list[str]) -> None:
    print("PolePosition project lifecycle CLI for FastAPI projects.\n")
    print("Usage: polepos <command> [options]\n")
    print("Commands:")

    for cmd in registry.all():
        aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
        print(f"  {cmd.name:<12} {cmd.description}{aliases}")


command = Command(
    name="help",
    aliases=("-h", "--help"),
    handler=run,
    description="Show help message",
)
