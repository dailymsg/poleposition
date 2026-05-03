import pytest

from pole_position.cli.services.integration_creator import (
    _kafka_integration_files,
    _rabbitmq_integration_files,
)
from pole_position.cli.services.integration_specs import (
    CHECKED_INTEGRATION_CONTRACTS,
    CREATABLE_INTEGRATION_CONTRACTS,
    KAFKA_INTEGRATION_CONTRACT,
    LLM_INTEGRATION_CONTRACT,
    RABBITMQ_INTEGRATION_CONTRACT,
    SUPPORTED_INTEGRATIONS,
    get_creatable_integration_contract,
)
from pole_position.cli.services.module_templates import llm_integration_files


def test_supported_integrations_come_from_creatable_contracts() -> None:
    assert SUPPORTED_INTEGRATIONS == ("kafka", "rabbitmq")
    assert tuple(contract.name for contract in CREATABLE_INTEGRATION_CONTRACTS) == (
        "kafka",
        "rabbitmq",
    )
    assert tuple(contract.name for contract in CHECKED_INTEGRATION_CONTRACTS) == (
        "kafka",
        "rabbitmq",
        "llm",
    )


def test_generated_integration_files_match_contracts() -> None:
    kafka_files = _kafka_integration_files("shop_api")
    rabbitmq_files = _rabbitmq_integration_files("shop_api")
    llm_files = llm_integration_files("shop_api")

    assert tuple(kafka_files) == KAFKA_INTEGRATION_CONTRACT.file_names
    assert tuple(rabbitmq_files) == RABBITMQ_INTEGRATION_CONTRACT.file_names
    assert tuple(llm_files) == LLM_INTEGRATION_CONTRACT.file_names
    assert "{{" not in "\n".join(kafka_files.values())
    assert "}}" not in "\n".join(kafka_files.values())
    assert "{{" not in "\n".join(rabbitmq_files.values())
    assert "}}" not in "\n".join(rabbitmq_files.values())


def test_non_creatable_integration_is_not_accepted_by_add_command_contract() -> None:
    with pytest.raises(ValueError) as exc_info:
        get_creatable_integration_contract("llm")

    assert "Unsupported integration 'llm'" in str(exc_info.value)
