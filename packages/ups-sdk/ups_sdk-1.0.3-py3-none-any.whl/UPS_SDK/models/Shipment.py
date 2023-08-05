from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from UPS_SDK.models.Package import Package
from UPS_SDK.models.ShipTo import ShipTo
from UPS_SDK.models.Shipper import Shipper
from UPS_SDK.models.ReferenceNumberItem import ReferenceNumberItem
from UPS_SDK.models.Service import Service
from UPS_SDK.models.ShipmentWeight import ShipmentWeight

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