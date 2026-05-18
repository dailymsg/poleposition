from pole_position.cli.services.module_templates.naming import to_class_name
from pole_position.cli.services.module_templates.renderer import render_template
from pole_position.cli.services.module_templates.spec import CRUD_MODULE_TEMPLATE_CONTRACT
from pole_position.cli.services.module_templates.spec import ModuleTemplate


def build_crud_template(*, package_name: str, module_name: str) -> ModuleTemplate:
    class_name = to_class_name(module_name)
    context = {
        "package_name": package_name,
        "module_name": module_name,
        "class_name": class_name,
    }

    return ModuleTemplate(
        files={
            "__init__.py": render_template("crud/__init__.py.tpl", context),
            "model.py": render_template("crud/model.py.tpl", context),
            "repository.py": render_template("crud/repository.py.tpl", context),
            "schemas.py": render_template("crud/schemas.py.tpl", context),
            "services/__init__.py": render_template(
                "crud/services/__init__.py.tpl",
                context,
            ),
            f"services/{module_name}_crud_service.py": render_template(
                "crud/services/module_crud_service.py.tpl",
                context,
            ),
            "router.py": render_template("crud/router.py.tpl", context),
        },
        integration_test_name=CRUD_MODULE_TEMPLATE_CONTRACT.integration_test_name(
            module_name
        ),
        integration_test_content=render_template(
            "crud/tests/integration.py.tpl",
            context,
        ),
        unit_test_name=CRUD_MODULE_TEMPLATE_CONTRACT.unit_test_name(module_name),
        unit_test_content=render_template(
            "crud/tests/unit.py.tpl",
            context,
        ),
        update_db_models=CRUD_MODULE_TEMPLATE_CONTRACT.update_db_models,
        ensure_llm_integrations=CRUD_MODULE_TEMPLATE_CONTRACT.ensure_llm_integrations,
        ensure_llm_settings=CRUD_MODULE_TEMPLATE_CONTRACT.ensure_llm_settings,
    )
