from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models import Response, Shipment

class TrackResponse(BaseModel):
    Response: Response
    Shipment: Shipment