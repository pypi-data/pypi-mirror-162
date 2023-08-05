from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.hpo_job_state import HPOJobState


class HPOJobGet(base_model.BaseModel):
    """HPO job schema for get responses."""

    object_: Literal["HPOJob"] = Field(..., alias="object")
    uuid: str
    create_time: str
    hpo: str
    creator: str
    schedule_time: str
    state: HPOJobState
    num_trials_completed: int
    update_time: Optional[str] = None
    detail: Optional[str] = None
    result: Optional[str] = None
