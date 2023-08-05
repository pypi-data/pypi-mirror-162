from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class HyperoptCreate(base_model.BaseModel):
    """Hyperopt search algorithm schema for create requests.

    See https://hyperopt.github.io/hyperopt/ for `hyperopt` reference."""

    object_: Optional[Literal["SearchAlgorithm"]] = Field(..., alias="object")
    type: Optional[Literal["Hyperopt"]] = "Hyperopt"
    metric: Optional[Literal["mse"]] = "mse"
    num_trials: Optional[int] = 10
    max_concurrent_trials: Optional[int] = 1
    algorithm: Optional[Literal["TPE"]] = "TPE"
    n_startup_jobs: Optional[int] = None
