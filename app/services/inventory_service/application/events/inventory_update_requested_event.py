from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from app.shared.application.events.event_bus import Event


@dataclass
class InventoryUpdateRequestedEvent(Event):
    product_id: UUID
    price: float
    quantity: int
    max_stock: int
    min_stock: int        
    expiry_date: date    
    id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None