from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from uuid import UUID

from app.services.order_service.domain.value_objects.order_status import OrderStatus

@dataclass
class BulkUpdateOrderItemResult:
    """Result for a single order update in a bulk operation"""
    order_id: UUID
    success: bool
    old_status: Optional[OrderStatus] = None
    new_status: Optional[OrderStatus] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None

@dataclass
class BulkUpdateOrderResponse:
    """Response for bulk order update operation"""
    total_attempted: int
    total_successful: int
    total_failed: int
    results: List[BulkUpdateOrderItemResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_attempted == 0:
            return 0.0
        return (self.total_successful / self.total_attempted) * 100
    
    def get_successful_orders(self) -> List[UUID]:
        """Get list of successfully updated order IDs"""
        return [result.order_id for result in self.results if result.success]
    
    def get_failed_orders(self) -> List[UUID]:
        """Get list of failed order IDs"""
        return [result.order_id for result in self.results if not result.success]
    
    def get_errors_summary(self) -> Dict[str, int]:
        """Get summary of error types"""
        error_counts = {}
        for result in self.results:
            if not result.success and result.error_code:
                error_counts[result.error_code] = error_counts.get(result.error_code, 0) + 1
        return error_counts 