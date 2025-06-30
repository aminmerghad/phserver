from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.services.order_service.domain.value_objects.order_status import OrderStatus


@dataclass
class CreateOrderItemDTO:
    product_id: UUID
    # name: str
    quantity: int
    price: Decimal

@dataclass
class CreateOrderDTO:
    user_id: UUID
    items: List[CreateOrderItemDTO]
    notes: Optional[str] = None

@dataclass
class OrderItemDTO:
    id: UUID
    product_id: UUID
    name: str
    quantity: int
    price: Decimal
    total_price: Decimal

@dataclass
class OrderDTO:
    order_id: UUID
    user_id: UUID
    status: str
    total_amount: Decimal
    items: List[dict]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    consumer_name: Optional[str] = None
    health_center_name: Optional[str] = None

@dataclass
class CreateOrderResponse:
    order : OrderDTO

@dataclass
class OrderSummaryDTO:
    order_id: UUID
    consumer_id: UUID
    status: str
    total_amount: Decimal
    items_count: int
    created_at: datetime
    items: List[dict]
    consumer_name: Optional[str] = None
    health_center_name: Optional[str] = None

@dataclass
class OrderFilterPaginationDTO:
    page: int
    per_page: int
    pages:int
    total:int




@dataclass
class OrderFilterResponseDTO:
    orders: List[OrderSummaryDTO]
    pagination: OrderFilterPaginationDTO
               

@dataclass
class OrderFilterDTO:
    page: int = 1
    per_page: int = 10
    user_id: Optional[UUID] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None 