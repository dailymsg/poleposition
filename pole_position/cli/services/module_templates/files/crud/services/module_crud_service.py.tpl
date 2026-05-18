from sqlalchemy.orm import Session

from {{package_name}}.bootstrap.logging import get_logger
from {{package_name}}.domain.exceptions import NotFoundError
from {{package_name}}.modules.{{module_name}}.model import {{class_name}}
from {{package_name}}.modules.{{module_name}}.repository import {{class_name}}Repository
from {{package_name}}.modules.{{module_name}}.schemas import (
    {{class_name}}Create,
    {{class_name}}Update,
)


logger = get_logger(__name__)


class {{class_name}}CrudService:
    def __init__(self, db: Session) -> None:
        self.repository = {{class_name}}Repository(db)

    def list_{{module_name}}(self) -> list[{{class_name}}]:
        logger.info("Listing {{module_name}}")
        return self.repository.list()

    def get_{{module_name}}(self, item_id: int) -> {{class_name}}:
        item = self.repository.get(item_id)
        if item is None:
            raise NotFoundError("{{class_name}} not found.")
        return item

    def create_{{module_name}}(self, payload: {{class_name}}Create) -> {{class_name}}:
        logger.info("Creating {{module_name}}", extra={"item_name": payload.name})
        return self.repository.create(name=payload.name)

    def update_{{module_name}}(
        self,
        item_id: int,
        payload: {{class_name}}Update,
    ) -> {{class_name}}:
        logger.info("Updating {{module_name}}", extra={"item_id": item_id})
        item = self.get_{{module_name}}(item_id)
        return self.repository.update(item, name=payload.name)

    def delete_{{module_name}}(self, item_id: int) -> None:
        logger.info("Deleting {{module_name}}", extra={"item_id": item_id})
        item = self.get_{{module_name}}(item_id)
        self.repository.delete(item)
