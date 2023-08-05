from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from UPS_SDK.models import (
    Package, ShipTo, Shipper,
    ReferenceNumberItem, Service, ShipmentWeight)

class Shipment(BaseModel):
    Shipper: Shipper
    ShipTo: ShipTo
    ShipmentWeight: ShipmentWeight
    Service: Service
    ReferenceNumbers: List[ReferenceNumberItem] = Field(None, alias="ReferenceNumber")
    ShipmentIdentificationNumber: str
    PickupDate: str
    ScheduledDeliveryDate: Optional[str]
    Package: Package