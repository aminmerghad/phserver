from dataclasses import dataclass
from uuid import UUID
from app.shared.application.events.event_bus import Event


@dataclass
class StockReceived(Event):
    product_id: UUID
    quantity: int
