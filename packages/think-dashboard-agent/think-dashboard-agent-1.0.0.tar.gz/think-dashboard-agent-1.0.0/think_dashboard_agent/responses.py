from typing import Union

from pydantic import BaseModel


class InstanceCheckResult(BaseModel):
    status: int = 200
    data: Union[Union[Union[dict, list], str], None] = None
    error: str = None
