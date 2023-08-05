from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from . import Address

class ActivityLocation(BaseModel):
    Address: Optional[Address]