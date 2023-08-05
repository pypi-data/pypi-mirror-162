from __future__ import annotations
from pydantic import BaseModel
from .Response import Response
from .Shipment import Shipment

class TrackResponse(BaseModel):
    Response: Response
    Shipment: Shipment