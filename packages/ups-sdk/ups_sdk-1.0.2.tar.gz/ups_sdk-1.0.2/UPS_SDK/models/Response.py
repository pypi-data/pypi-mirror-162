from __future__ import annotations
from pydantic import BaseModel
from UPS_SDK.models import TransactionReference

class Response(BaseModel):
    TransactionReference: TransactionReference
    ResponseStatusCode: str
    ResponseStatusDescription: str