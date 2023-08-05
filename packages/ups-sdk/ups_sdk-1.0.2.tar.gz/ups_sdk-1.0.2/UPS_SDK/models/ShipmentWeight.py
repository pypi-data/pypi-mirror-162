from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models import UnitOfMeasurement
class ShipmentWeight(BaseModel):
    UnitOfMeasurement: UnitOfMeasurement
    Weight: str
