from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models import Address
class ShipTo(BaseModel):
    Address: Address