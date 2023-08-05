from myst.models import base_model


class ShareableResourceUnshare(base_model.BaseModel):
    """Schema for unshare requests."""

    accessor: str
