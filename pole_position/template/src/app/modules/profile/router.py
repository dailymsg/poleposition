from fastapi import APIRouter, Depends

from {{project_import_name}}.api.deps import get_current_user, require_roles
from {{project_import_name}}.auth.schemas import AuthenticatedUser
from {{project_import_name}}.modules.profile.schemas import ProfileResponse


router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def read_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ProfileResponse:
    return ProfileResponse(
        subject=current_user.subject,
        email=current_user.email,
        roles=current_user.roles,
    )


@router.get("/admin-preview", response_model=ProfileResponse)
def read_admin_preview(
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> ProfileResponse:
    return ProfileResponse(
        subject=current_user.subject,
        email=current_user.email,
        roles=current_user.roles,
    )
