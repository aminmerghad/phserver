from dataclasses import dataclass
from app.shared.application.events.event_bus import Event


@dataclass
class StockReleaseRequestedEvent(Event):
    order_id: str
    items: list[dict]

@dataclass
class StockReleaseFailedEvent(Event):
    order_id: str
    items: list[dict]

