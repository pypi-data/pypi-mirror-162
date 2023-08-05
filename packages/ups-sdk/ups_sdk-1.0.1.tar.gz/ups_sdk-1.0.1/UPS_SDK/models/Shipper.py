from __future__ import annotations
from pydantic import BaseModel
from . import Address

class Shipper(BaseModel):
    ShipperNumber: str
    Address: Address