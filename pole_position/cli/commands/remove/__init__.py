from pole_position.cli.command import Command
from pole_position.cli.commands.remove.module import command as module_cmd
from pole_position.cli.registry import CommandRegistry


subcommands = CommandRegistry()
subcommands.register(module_cmd)


def run(args: list[str]) -> None:
    print("Usage: polepos remove <subcommand>\n")
    print("Subcommands:")

    for command in subcommands.all():
        aliases = f" ({', '.join(command.aliases)})" if command.aliases else ""
        print(f"  {command.name:<12} {command.description}{aliases}")


command = Command(
    name="remove",
    handler=run,
    description="Remove generated resources from the current project",
    subcommands=subcommands,
)
