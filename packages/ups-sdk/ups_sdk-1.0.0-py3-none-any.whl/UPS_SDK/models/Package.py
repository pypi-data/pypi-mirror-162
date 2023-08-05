from __future__ import annotations
from pydantic import BaseModel, Field
from .ActivityItem import ActivityItem
from .Message import Message
from .PackageWeight import PackageWeight
from .ReferenceNumber import ReferenceNumber
from typing import List, Optional

class Package(BaseModel):
    TrackingNumber: str
    DeliveryIndicator: str
    RescheduledDeliveryDate: Optional[str]
    AllActivity: List[ActivityItem] = Field(None, alias="Activity")
    Message: Optional[Message]
    PackageWeight: PackageWeight
    ReferenceNumber: ReferenceNumber
    
    @property
    def get_US_activities(self) -> List[ActivityItem]:
        activities = []
        for activity in self.AllActivity:
            if activity.ActivityLocation is not None and activity.ActivityLocation.Address is not None and activity.ActivityLocation.Address.CountryCode == "US":
                activities.append(activity)
        return activities