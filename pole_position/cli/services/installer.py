import os
import shutil
import subprocess
import venv
from pathlib import Path


def install_project_dependencies(project_path: Path) -> str:
    if shutil.which("uv") is not None:
        return _install_with_uv(project_path)

    return _install_with_pip(project_path)


def _install_with_uv(project_path: Path) -> str:
    try:
        subprocess.run(
            ["uv", "sync"],
            cwd=project_path,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Dependency installation failed with uv in {project_path}"
        ) from exc

    return "uv"


def _install_with_pip(project_path: Path) -> str:
    venv_path = project_path / ".venv"
    python = _venv_python(venv_path)

    try:
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(venv_path)

        subprocess.run(
            [str(python), "-m", "pip", "install", "-e", ".[dev]"],
            cwd=project_path,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Dependency installation failed with pip in {project_path}"
        ) from exc

    return "pip"


def _venv_python(venv_path: Path) -> Path:
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"

    return venv_path / "bin" / "python"
