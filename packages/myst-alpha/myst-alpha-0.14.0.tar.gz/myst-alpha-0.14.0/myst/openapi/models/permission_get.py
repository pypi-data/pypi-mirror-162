from myst.models import base_model
from myst.openapi.models.operation import Operation


class PermissionGet(base_model.BaseModel):
    """Schema for permission get responses."""

    operation: Operation
