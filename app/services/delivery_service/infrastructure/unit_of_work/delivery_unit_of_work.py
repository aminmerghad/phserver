from typing import Any

from app.services.delivery_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.delivery_service.domain.ports.outgoing_ports import OrderServicePort, AuthServicePort
from app.services.delivery_service.infrastructure.adapters.outgoing.delivery_adapter import (
    DeliveryOrderServiceAdapter,
    DeliveryAuthServiceAdapter
)
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus


class DeliveryUnitOfWork(UnitOfWork):
    """Concrete implementation of Unit of Work for delivery service"""
    
    def __init__(self, event_bus: EventBus, acl: UnifiedACL):
        self._event_bus = event_bus
        self._acl = acl
        self._order_service_port = None
        self._auth_service_port = None
    
    @property
    def order_service_port(self) -> OrderServicePort:
        """Get the order service port"""
        if not self._order_service_port:
            self._order_service_port = DeliveryOrderServiceAdapter(self._acl)
        return self._order_service_port
    
    @property
    def auth_service_port(self) -> AuthServicePort:
        """Get the auth service port"""
        if not self._auth_service_port:
            self._auth_service_port = DeliveryAuthServiceAdapter(self._acl)
        return self._auth_service_port
    
    def __enter__(self):
        """Enter the context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        if exc_type:
            self.rollback()
        else:
            self.commit()
    
    def commit(self) -> None:
        """Commit any changes (delivery service doesn't persist data directly)"""
        pass
    
    def rollback(self) -> None:
        """Rollback any changes (delivery service doesn't persist data directly)"""
        pass
    
    def publish(self, event: Any) -> None:
        """Publish an event"""
        if self._event_bus:
            self._event_bus.publish(event) 