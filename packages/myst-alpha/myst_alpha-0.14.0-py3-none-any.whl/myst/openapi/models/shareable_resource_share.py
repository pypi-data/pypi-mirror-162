from myst.models import base_model
from myst.openapi.models.operation import Operation


class ShareableResourceShare(base_model.BaseModel):
    """Schema for share requests."""

    accessor: str
    access_level: Operation
