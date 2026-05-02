from pole_position.cli.services.module_templates.ai_prompt import build_ai_prompt_template
from pole_position.cli.services.module_templates.spec import ModuleTemplate
from pole_position.cli.services.module_templates.standard import build_standard_template


SUPPORTED_MODULE_TEMPLATES = ("standard", "ai-prompt")


def build_module_template(
    *,
    template: str,
    package_name: str,
    module_name: str,
) -> ModuleTemplate:
    if template == "standard":
        return build_standard_template(
            package_name=package_name,
            module_name=module_name,
        )

    if template == "ai-prompt":
        return build_ai_prompt_template(
            package_name=package_name,
            module_name=module_name,
        )

    supported = ", ".join(SUPPORTED_MODULE_TEMPLATES)
    raise ValueError(
        f"Unsupported module template '{template}'. Expected one of: {supported}."
    )
