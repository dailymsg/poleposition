from pole_position.cli.command import Command
from pole_position.cli.usage import print_help_topic


def run(args: list[str]) -> None:
    print_help_topic(args)


command = Command(
    name="help",
    aliases=("-h", "--help"),
    handler=run,
    description="Show help message",
)
