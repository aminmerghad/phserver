from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.services.delivery_service.domain.enums.delivery_status import DeliveryStatus


@dataclass
class DeliveryLocationDto:
    """DTO for delivery location information"""
    health_care_center_id: UUID
    health_care_center_name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    email: Optional[str] = None


@dataclass
class DeliveryOrderDto:
    """DTO for order information in delivery context"""
    order_id: UUID
    user_id: UUID
    total_amount: float
    items_count: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class DeliveryRouteDto:
    """DTO for delivery route information"""
    id: Optional[UUID] = None
    route_name: str = ""
    orders: List[DeliveryOrderDto] = None
    location: Optional[DeliveryLocationDto] = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    estimated_delivery_time: Optional[datetime] = None
    total_amount: float = 0.0
    total_items_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.orders is None:
            self.orders = []


@dataclass
class DeliveryRoutesResponseDto:
    """DTO for delivery routes response"""
    routes: List[DeliveryRouteDto]
    total_routes: int
    processing_orders_count: int
    total_estimated_deliveries: int
    
    
@dataclass
class ProcessingOrderDto:
    """DTO for processing order from order service"""
    order_id: UUID
    user_id: UUID
    status: str
    total_amount: float
    items_count: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class PrioritizedOrderDto:
    """DTO for prioritized order from order service (SHIPPED first, then PROCESSING)"""
    order_id: UUID
    user_id: UUID
    status: str
    total_amount: float
    items_count: int
    priority: str  # 'HIGH' for SHIPPED, 'NORMAL' for PROCESSING
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class HealthCareCenterDto:
    """DTO for health care center from auth service"""
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    latitude: float
    longitude: float
    is_active: bool 