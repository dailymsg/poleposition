from fastapi import APIRouter, Depends{{router_query_import}}, status
from sqlalchemy.orm import Session

from {{package_name}}.api.deps import {{router_api_deps_imports}}
from {{package_name}}.modules.{{module_name}}.schemas import (
{{router_schema_imports}}
)
from {{package_name}}.modules.{{module_name}}.services import {{class_name}}CrudService


router = APIRouter({{router_dependencies}})


@router.get("/", response_model={{router_list_response_model}})
def list_{{module_name}}(
{{router_list_parameters}}) -> {{router_list_response_model}}:
    return {{class_name}}CrudService(db).list_{{module_name}}({{router_list_call_args}})


@router.post("/", response_model={{class_name}}Read, status_code=status.HTTP_201_CREATED)
def create_{{module_name}}(
{{router_create_parameters}}) -> {{class_name}}Read:
    return {{class_name}}CrudService(db).create_{{module_name}}(payload)


@router.get("/{item_id}", response_model={{class_name}}Read)
def get_{{module_name}}(
{{router_get_parameters}}) -> {{class_name}}Read:
    return {{class_name}}CrudService(db).get_{{module_name}}({{router_get_call_args}})


@router.patch("/{item_id}", response_model={{class_name}}Read)
def update_{{module_name}}(
{{router_update_parameters}}) -> {{class_name}}Read:
    return {{class_name}}CrudService(db).update_{{module_name}}({{router_update_call_args}})


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{{module_name}}(
{{router_delete_parameters}}) -> None:
    {{class_name}}CrudService(db).delete_{{module_name}}({{router_delete_call_args}})
