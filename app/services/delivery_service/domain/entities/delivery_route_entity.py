from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.services.delivery_service.domain.enums.delivery_status import DeliveryStatus


@dataclass
class DeliveryLocationEntity:
    """Represents a delivery location with GPS coordinates"""
    health_care_center_id: UUID
    health_care_center_name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    email: Optional[str] = None


@dataclass
class DeliveryOrderEntity:
    """Represents an order in a delivery route"""
    order_id: UUID
    user_id: UUID
    total_amount: float
    items_count: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class DeliveryRouteEntity:
    """Main entity representing a delivery route"""
    id: Optional[UUID] = None
    route_name: str = ""
    orders: List[DeliveryOrderEntity] = None
    location: Optional[DeliveryLocationEntity] = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    estimated_delivery_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.orders is None:
            self.orders = []
        if not self.route_name and self.location:
            self.route_name = f"Route to {self.location.health_care_center_name}"
    
    def add_order(self, order: DeliveryOrderEntity) -> None:
        """Add an order to the delivery route"""
        if order not in self.orders:
            self.orders.append(order)
            self.updated_at = datetime.utcnow()
    
    def get_total_amount(self) -> float:
        """Calculate total amount for all orders in the route"""
        return sum(order.total_amount for order in self.orders)
    
    def get_total_items_count(self) -> int:
        """Calculate total items count for all orders in the route"""
        return sum(order.items_count for order in self.orders)
    
    def can_add_order(self, order: DeliveryOrderEntity) -> bool:
        """Check if an order can be added to this route (same location)"""
        if not self.location:
            return True
        # For now, we'll group orders by health care center
        # Future: Could implement more sophisticated route optimization
        return True
    
    def update_status(self, new_status: DeliveryStatus) -> None:
        """Update delivery route status"""
        self.status = new_status
        self.updated_at = datetime.utcnow() 