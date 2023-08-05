from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models.UnitOfMeasurement1 import UnitOfMeasurement1
class PackageWeight(BaseModel):
    UnitOfMeasurement: UnitOfMeasurement1
    Weight: str