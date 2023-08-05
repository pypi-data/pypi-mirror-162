from __future__ import annotations
from pydantic import BaseModel
from . import Response, Shipment

class TrackResponse(BaseModel):
    Response: Response
    Shipment: Shipment