from pathlib import Path
import os
import py_compile
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


def _assert_python_files_compile(project_root: Path) -> None:
    for path in sorted(project_root.rglob("*.py")):
        py_compile.compile(str(path), doraise=True)


def test_add_auth_creates_auth_workflow_and_wiring(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp")
    assert create_result.returncode == 0

    project_root = tmp_path / "myapp"
    result = run_cli(project_root, "add", "auth")

    assert result.returncode == 0
    assert "Added auth workflow" in result.stdout

    package_root = project_root / "src" / "myapp"
    auth_root = package_root / "auth"
    expected_files = [
        auth_root / "model.py",
        auth_root / "password.py",
        auth_root / "repository.py",
        auth_root / "router.py",
        auth_root / "user_schemas.py",
        auth_root / "user_service.py",
        project_root / "tests" / "integration" / "test_auth.py",
        project_root / "tests" / "unit" / "test_auth_service.py",
    ]
    for path in expected_files:
        assert path.exists(), f"Expected generated auth file is missing: {path}"

    router_content = (package_root / "api" / "router.py").read_text(encoding="utf-8")
    models_content = (package_root / "db" / "models.py").read_text(encoding="utf-8")
    pyproject_content = (project_root / "pyproject.toml").read_text(encoding="utf-8")
    manifest = (project_root / ".poleposition.toml").read_text(encoding="utf-8")

    assert "from myapp.auth.router import router as auth_router" in router_content
    assert 'api_router.include_router(auth_router, prefix="/auth", tags=["auth"])' in router_content
    assert "from myapp.auth import model as auth_model  # noqa: F401" in models_content
    assert '"pwdlib[argon2]>=0.2.0",' in pyproject_content
    assert "auth = true" in manifest
    assert "{{" not in (auth_root / "router.py").read_text(encoding="utf-8")
    _assert_python_files_compile(project_root)


def test_add_auth_rejects_duplicate_workflow(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp")
    assert create_result.returncode == 0

    project_root = tmp_path / "myapp"
    first_result = run_cli(project_root, "add", "auth")
    second_result = run_cli(project_root, "add", "auth")

    assert first_result.returncode == 0
    assert second_result.returncode != 0
    assert "Generated auth file already exists" in second_result.stdout


def test_add_auth_rejects_database_free_project(tmp_path: Path) -> None:
    create_result = run_cli(tmp_path, "start", "myapp", "--db", "none")
    assert create_result.returncode == 0

    project_root = tmp_path / "myapp"
    result = run_cli(project_root, "add", "auth")

    assert result.returncode != 0
    assert "Auth workflow requires generated db/ wiring" in result.stdout
