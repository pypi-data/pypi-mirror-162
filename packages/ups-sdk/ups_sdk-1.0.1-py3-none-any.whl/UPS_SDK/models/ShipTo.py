from __future__ import annotations
from pydantic import BaseModel
from . import Address
class ShipTo(BaseModel):
    Address: Address