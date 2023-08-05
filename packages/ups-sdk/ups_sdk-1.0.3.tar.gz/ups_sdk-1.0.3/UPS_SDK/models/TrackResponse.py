from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models.Response import Response
from UPS_SDK.models.Shipment import Shipment

class TrackResponse(BaseModel):
    Response: Response
    Shipment: Shipment