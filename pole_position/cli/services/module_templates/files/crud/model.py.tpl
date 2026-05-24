{{model_datetime_import}}from sqlalchemy import {{model_sqlalchemy_imports}}
from sqlalchemy.orm import Mapped, mapped_column

from {{package_name}}.db.base import Base
{{model_utc_now}}


class {{class_name}}(Base):
    __tablename__ = "{{module_name}}"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
{{model_tenant_field}}    name: Mapped[str] = mapped_column(String(120), index=True)
{{model_timestamp_fields}}{{model_soft_delete_field}}
