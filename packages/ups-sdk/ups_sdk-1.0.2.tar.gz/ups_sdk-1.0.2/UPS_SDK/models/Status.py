from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models import StatusType, StatusCode
class Status(BaseModel):
    StatusType: StatusType
    StatusCode: StatusCode