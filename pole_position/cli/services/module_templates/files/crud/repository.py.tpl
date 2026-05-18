from sqlalchemy import select
from sqlalchemy.orm import Session

from {{package_name}}.modules.{{module_name}}.model import {{class_name}}


class {{class_name}}Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[{{class_name}}]:
        statement = select({{class_name}}).order_by({{class_name}}.id.asc())
        return list(self.db.scalars(statement))

    def get(self, item_id: int) -> {{class_name}} | None:
        return self.db.get({{class_name}}, item_id)

    def create(self, *, name: str) -> {{class_name}}:
        item = {{class_name}}(name=name)
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
        self.db.delete(item)
        self.db.commit()
