from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleTemplate:
    files: dict[str, str]
    integration_test_name: str
    integration_test_content: str
    unit_test_name: str
    unit_test_content: str
    update_db_models: bool = True
    ensure_llm_integrations: bool = False
    ensure_llm_settings: bool = False
