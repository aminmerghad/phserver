from dataclasses import dataclass
from app.shared.application.events.event_bus import Event


@dataclass
class OrderCreatedEvent(Event):
    order_id: str 

    def to_dict(self):
        return {
            'event_type': self.metadata.event_type,
            'order_id': self.order_id
        }
