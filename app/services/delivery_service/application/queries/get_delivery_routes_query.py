from dataclasses import dataclass
from typing import Optional


@dataclass
class GetDeliveryRoutesQuery:
    """Query to get delivery routes for processing orders"""
    include_location_details: bool = True
    group_by_location: bool = True
    limit: Optional[int] = None
    
    def __post_init__(self):
        """Validate query parameters"""
        if self.limit is not None and self.limit <= 0:
            raise ValueError("Limit must be greater than 0") 