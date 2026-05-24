{{schemas_datetime_import}}from pydantic import BaseModel, ConfigDict, Field


class {{class_name}}Create(BaseModel):
{{schemas_create_fields}}


class {{class_name}}Update(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)


class {{class_name}}Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)

{{schemas_read_fields}}{{schemas_page_class}}
