{{repository_datetime_import}}from sqlalchemy import {{repository_sqlalchemy_imports}}
from sqlalchemy.orm import Session

from {{package_name}}.modules.{{module_name}}.model import {{class_name}}
{{repository_utc_now}}


class {{class_name}}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self{{repository_list_parameters}}) -> list[{{class_name}}]:
        statement = select({{class_name}})
{{repository_list_filters}}        statement = statement.order_by({{class_name}}.id.asc())
{{repository_pagination_clause}}        return list(self.db.scalars(statement))

{{repository_count_method}}
    def get(self, item_id: int{{repository_get_parameters}}) -> {{class_name}} | None:
        statement = select({{class_name}}).where({{class_name}}.id == item_id)
{{repository_get_filters}}        return self.db.scalar(statement)

    def create(self{{repository_create_parameters}}) -> {{class_name}}:
        item = {{class_name}}(
{{repository_create_fields}}        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: {{class_name}}, *, name: str | None) -> {{class_name}}:
        if name is not None:
            item.name = name
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: {{class_name}}) -> None:
{{repository_delete_body}}
