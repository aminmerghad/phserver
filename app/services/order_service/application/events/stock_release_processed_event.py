from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any
from app.shared.application.events.event_bus import Event


@dataclass
class StockReleaseProcessedEvent(Event):
    """
    Event received when inventory service has processed a stock release request.
    Contains the results of the stock release operation.
    """
    order_id: str
    success: bool
    items: List[Dict[str, Any]]
    timestamp: str = None
    
    def __post_init__(self):
        super().__post_init__()  # Call the parent's __post_init__
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat() 