from abc import ABC, abstractmethod
from typing import Any

from app.services.delivery_service.domain.ports.outgoing_ports import OrderServicePort, AuthServicePort


class UnitOfWork(ABC):
    """Unit of Work interface for managing delivery service dependencies"""
    
    @property
    @abstractmethod
    def order_service_port(self) -> OrderServicePort:
        """Get the order service port"""
        pass
    
    @property
    @abstractmethod
    def auth_service_port(self) -> AuthServicePort:
        """Get the auth service port"""
        pass
    
    @abstractmethod
    def __enter__(self):
        """Enter the context manager"""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Commit any changes"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback any changes"""
        pass
    
    @abstractmethod
    def publish(self, event: Any) -> None:
        """Publish an event"""
        pass 