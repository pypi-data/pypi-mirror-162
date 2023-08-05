from myst.models import base_model
from myst.openapi.models.alias_get_type import AliasGetType


class AliasGet(base_model.BaseModel):
    """Schema for Alias get responses."""

    alias: str
    type: AliasGetType
    subject: str
