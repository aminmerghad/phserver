from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from app.services.order_service.domain.value_objects.order_status import OrderStatus

@dataclass
class BulkUpdateOrderItemCommand:
    """Command for updating a single order in a bulk operation"""
    order_id: UUID
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

@dataclass
class BulkUpdateOrderCommand:
    """Command for bulk updating multiple orders"""
    updates: List[BulkUpdateOrderItemCommand]
    update_by: Optional[UUID] = None  # User who is performing the update
    
    def __post_init__(self):
        if not self.updates:
            raise ValueError("At least one order update is required")
        
        if len(self.updates) > 100:  # Prevent too large bulk operations
            raise ValueError("Maximum 100 orders can be updated in a single bulk operation") 