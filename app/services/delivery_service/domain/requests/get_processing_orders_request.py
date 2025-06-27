from dataclasses import dataclass
from typing import Optional


@dataclass
class GetProcessingOrdersRequest:
    """Request to get orders with PROCESSING status"""
    status: str = "PROCESSING"
    limit: Optional[int] = None
    include_details: bool = True 