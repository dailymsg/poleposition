from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from {{package_name}}.api.deps import db_session
from {{package_name}}.modules.{{module_name}}.schemas import (
    {{class_name}}Create,
    {{class_name}}Read,
    {{class_name}}Update,
)
from {{package_name}}.modules.{{module_name}}.services import {{class_name}}CrudService


router = APIRouter()


@router.get("/", response_model=list[{{class_name}}Read])
def list_{{module_name}}(db: Session = Depends(db_session)) -> list[{{class_name}}Read]:
    return {{class_name}}CrudService(db).list_{{module_name}}()


@router.post("/", response_model={{class_name}}Read, status_code=status.HTTP_201_CREATED)
def create_{{module_name}}(payload: {{class_name}}Create, db: Session = Depends(db_session)) -> {{class_name}}Read:
    return {{class_name}}CrudService(db).create_{{module_name}}(payload)


@router.get("/{item_id}", response_model={{class_name}}Read)
def get_{{module_name}}(item_id: int, db: Session = Depends(db_session)) -> {{class_name}}Read:
    return {{class_name}}CrudService(db).get_{{module_name}}(item_id)


@router.patch("/{item_id}", response_model={{class_name}}Read)
def update_{{module_name}}(
    item_id: int,
    payload: {{class_name}}Update,
    db: Session = Depends(db_session),
) -> {{class_name}}Read:
    return {{class_name}}CrudService(db).update_{{module_name}}(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{{module_name}}(item_id: int, db: Session = Depends(db_session)) -> None:
    {{class_name}}CrudService(db).delete_{{module_name}}(item_id)
