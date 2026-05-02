from pathlib import Path
import os
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(REPO_ROOT)
    )

    return subprocess.run(
        [sys.executable, "-m", "pole_position.cli.main", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )


def test_check_passes_for_generated_project(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp")
    assert create_result.returncode == 0

    project_root = tmp_path / "myapp"
    result = run_cli(project_root, "check")

    assert result.returncode == 0
    assert "PolePosition project check passed." in result.stdout
    assert f"Project root: {project_root}" in result.stdout
    assert "Package: myapp" in result.stdout


def test_check_works_from_nested_directory(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp")
    assert create_result.returncode == 0

    nested_dir = tmp_path / "myapp" / "src" / "myapp" / "modules"
    result = run_cli(nested_dir, "check")

    assert result.returncode == 0
    assert "PolePosition project check passed." in result.stdout


def test_check_fails_outside_project(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "check")

    assert result.returncode != 0
    assert "does not look like a PolePosition project" in result.stdout


def test_check_reports_missing_managed_marker(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp")
    assert create_result.returncode == 0

    project_root = tmp_path / "myapp"
    router_path = project_root / "src" / "myapp" / "api" / "router.py"
    router_content = router_path.read_text(encoding="utf-8").replace(
        "# polepos:router-imports",
        "# router imports are managed manually",
    )
    router_path.write_text(router_content, encoding="utf-8")

    result = run_cli(project_root, "check")

    assert result.returncode != 0
    assert "PolePosition project check failed." in result.stdout
    assert "Managed marker '# polepos:router-imports' is missing" in result.stdout
    assert "api/router.py" in result.stdout


def test_check_reports_missing_alembic_config(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp")
    assert create_result.returncode == 0

    project_root = tmp_path / "myapp"
    (project_root / "alembic.ini").unlink()

    result = run_cli(project_root, "check")

    assert result.returncode != 0
    assert "PolePosition project check failed." in result.stdout
    assert "Required Alembic path is missing" in result.stdout
    assert "alembic.ini" in result.stdout


def test_check_rejects_unexpected_arguments(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "check", "--fix")

    assert result.returncode != 0
    assert "Unexpected argument: --fix" in result.stdout
    assert "Usage: polepos check" in result.stdout
