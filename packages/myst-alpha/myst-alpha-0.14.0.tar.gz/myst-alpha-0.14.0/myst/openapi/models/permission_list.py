from typing import List

from myst.models import base_model
from myst.openapi.models.permission_get import PermissionGet


class PermissionList(base_model.BaseModel):
    """Schema for permission list responses."""

    data: List[PermissionGet]
    has_more: bool
