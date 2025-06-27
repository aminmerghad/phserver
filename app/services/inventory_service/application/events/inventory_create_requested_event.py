from uuid import UUID
from datetime import date
from typing import Optional
from dataclasses import dataclass

from app.shared.application.events.event_bus import Event


@dataclass
class InventoryCreateRequestedEvent(Event):
    product_id: UUID
    price: float
    quantity: int
    max_stock: int
    min_stock: int        
    expiry_date: date    
    supplier_id: Optional[UUID] = None
