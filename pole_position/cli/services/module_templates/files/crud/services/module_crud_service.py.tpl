from sqlalchemy.orm import Session

from {{package_name}}.bootstrap.logging import get_logger
from {{package_name}}.domain.exceptions import NotFoundError
from {{package_name}}.modules.{{module_name}}.model import {{class_name}}
from {{package_name}}.modules.{{module_name}}.repository import {{class_name}}Repository
from {{package_name}}.modules.{{module_name}}.schemas import (
{{service_schema_imports}}
)


logger = get_logger(__name__)


class {{class_name}}CrudService:
    def __init__(self, db: Session) -> None:
        self.repository = {{class_name}}Repository(db)

    def list_{{module_name}}(self{{service_list_parameters}}) -> {{service_list_return_type}}:
{{service_list_body}}

    def get_{{module_name}}(self, item_id: int{{service_get_parameters}}) -> {{class_name}}:
        item = self.repository.get({{service_get_call_args}})
        if item is None:
            raise NotFoundError("{{class_name}} not found.")
        return item

    def create_{{module_name}}(self, payload: {{class_name}}Create) -> {{class_name}}:
        logger.info("Creating {{module_name}}", extra={"item_name": payload.name})
        return self.repository.create({{service_create_call_args}})

    def update_{{module_name}}(
        self,
        item_id: int,
        payload: {{class_name}}Update,
{{service_update_parameters}}    ) -> {{class_name}}:
        logger.info("Updating {{module_name}}", extra={"item_id": item_id})
        item = self.get_{{module_name}}({{service_update_get_args}})
        return self.repository.update(item, name=payload.name)

    def delete_{{module_name}}(self, item_id: int{{service_delete_parameters}}) -> None:
        logger.info("Deleting {{module_name}}", extra={"item_id": item_id})
        item = self.get_{{module_name}}({{service_delete_get_args}})
        self.repository.delete(item)
