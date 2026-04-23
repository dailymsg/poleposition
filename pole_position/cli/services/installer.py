import shutil
import subprocess
from pathlib import Path


def ensure_uv_installed() -> None:
    if shutil.which("uv") is None:
        raise RuntimeError(
            "`uv` is not installed or not available in PATH. "
            "Install uv first, or run the project setup manually."
        )


def install_project_dependencies(project_path: Path) -> None:
    ensure_uv_installed()

    try:
        subprocess.run(
            ["uv", "sync"],
            cwd=project_path,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Dependency installation failed in {project_path}"
        ) from exc