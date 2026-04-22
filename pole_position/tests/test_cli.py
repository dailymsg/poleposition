import subprocess
import sys

from pole_position import __version__


def test_cli_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pole_position.cli.main", "version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == __version__