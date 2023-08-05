from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from UPS_SDK.models import Address

class ActivityLocation(BaseModel):
    Address: Optional[Address]