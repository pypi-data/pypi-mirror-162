from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from .Package import Package
from .ShipTo import ShipTo
from .Shipper import Shipper
from .ReferenceNumberItem import ReferenceNumberItem
from .Service import Service
from .ShipmentWeight import ShipmentWeight

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