import subprocess
import sys

import pytest

from pole_position.cli.command import Command
from pole_position.cli.registry import CommandRegistry


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "pole_position.cli.main", *args],
        capture_output=True,
        text=True,
    )


def test_help_command():
    result = run_cli("help")
    assert result.returncode == 0
    assert "project lifecycle CLI" in result.stdout
    assert "Usage" in result.stdout
    assert "check" in result.stdout


def test_version_command():
    result = run_cli("version")
    assert result.returncode == 0


def test_version_help_shows_usage():
    result = run_cli("version", "--help")
    assert result.returncode == 0
    assert "Usage: polepos version" in result.stdout


def test_version_rejects_extra_argument():
    result = run_cli("version", "extra")
    assert result.returncode != 0
    assert "Unexpected argument: extra" in result.stdout
    assert "Usage: polepos version" in result.stdout


def test_unknown_command():
    result = run_cli("unknown")
    assert result.returncode != 0
    assert "Unknown command" in result.stdout


def test_command_registry_allows_idempotent_registration():
    registry = CommandRegistry()
    command = Command(
        name="example",
        aliases=("sample",),
        handler=lambda args: None,
        description="Example command",
    )

    registry.register(command)
    registry.register(command)

    assert registry.get("example") is command
    assert registry.get("sample") is command
    assert registry.all() == [command]


def test_command_registry_rejects_conflicting_registration():
    registry = CommandRegistry()
    command = Command(
        name="example",
        handler=lambda args: None,
        description="Example command",
    )
    conflicting_command = Command(
        name="example",
        handler=lambda args: None,
        description="Conflicting command",
    )

    registry.register(command)

    with pytest.raises(RuntimeError, match="Command already registered: example"):
        registry.register(conflicting_command)
