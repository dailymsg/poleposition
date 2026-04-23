from pathlib import Path

from pole_position.cli.commands.startproject import run


def test_startproject_creates_project(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    run(["myapp"])

    assert (tmp_path / "myapp").exists()
    assert (tmp_path / "myapp" / "pyproject.toml").exists()
    assert (tmp_path / "myapp" / "src" / "myapp").exists()


def test_startproject_with_install_flag_creates_project(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    called = {"value": False}

    def fake_install_project_dependencies(project_path: Path) -> None:
        called["value"] = True

    monkeypatch.setattr(
        "pole_position.cli.commands.startproject.install_project_dependencies",
        fake_install_project_dependencies,
    )

    run(["myapp", "--install"])

    assert (tmp_path / "myapp").exists()
    assert called["value"] is True