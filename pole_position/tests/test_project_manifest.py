from pathlib import Path

from pole_position.cli.services.project_manifest import ProjectManifest
from pole_position.cli.services.project_manifest import read_project_manifest
from pole_position.cli.services.project_manifest import record_manifest_integration
from pole_position.cli.services.project_manifest import record_manifest_module
from pole_position.cli.services.project_manifest import write_project_manifest


def test_manifest_keeps_quoted_false_integration_invalid_not_enabled(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / ".poleposition.toml"
    manifest_path.write_text(
        (
            '[poleposition]\n'
            'package = "myapp"\n'
            'db = "sqlite"\n'
            '\n'
            '[modules]\n'
            'status = "starter"\n'
            '\n'
            '[integrations]\n'
            'kafka = "false"\n'
            'rabbitmq = false\n'
            'llm = true\n'
        ),
        encoding="utf-8",
    )

    manifest = read_project_manifest(tmp_path)

    assert manifest.enabled_integrations == {
        "llm": True,
        "rabbitmq": False,
    }
    assert manifest.invalid_integration_values == {"kafka": '"false"'}


def test_manifest_preserves_invalid_integration_values_when_recording_module(
    tmp_path: Path,
) -> None:
    write_project_manifest(
        tmp_path,
        ProjectManifest(
            package_name="myapp",
            database="sqlite",
            modules={"status": "starter"},
            invalid_integrations={"kafka": '"false"'},
            exists=True,
        ),
    )

    record_manifest_module(
        project_root=tmp_path,
        module_name="garage",
        template="standard",
    )

    manifest_content = (tmp_path / ".poleposition.toml").read_text(encoding="utf-8")
    assert 'garage = "standard"' in manifest_content
    assert 'kafka = "false"' in manifest_content


def test_record_manifest_integration_replaces_invalid_integration_value(
    tmp_path: Path,
) -> None:
    write_project_manifest(
        tmp_path,
        ProjectManifest(
            package_name="myapp",
            database="sqlite",
            invalid_integrations={"kafka": '"false"'},
            exists=True,
        ),
    )

    record_manifest_integration(project_root=tmp_path, integration_name="kafka")

    manifest = read_project_manifest(tmp_path)
    assert manifest.enabled_integrations == {"kafka": True}
    assert manifest.invalid_integration_values == {}
