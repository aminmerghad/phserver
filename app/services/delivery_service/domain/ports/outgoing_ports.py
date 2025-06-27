from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.services.delivery_service.application.dtos.delivery_dto import ProcessingOrderDto, PrioritizedOrderDto, HealthCareCenterDto


class OrderServicePort(ABC):
    """Interface for communicating with Order Service"""
    
    @abstractmethod
    def get_processing_orders(self) -> List[ProcessingOrderDto]:
        """Get all orders with PROCESSING status"""
        pass
    
    @abstractmethod
    def get_prioritized_orders_for_delivery(self) -> List[PrioritizedOrderDto]:
        """Get prioritized orders for delivery (SHIPPED first, then PROCESSING)"""
        pass


class AuthServicePort(ABC):
    """Interface for communicating with Auth Service"""
    
    @abstractmethod
    def get_user_health_care_center(self, user_id: UUID) -> Optional[HealthCareCenterDto]:
        """Get health care center for a user"""
        pass
    
    @abstractmethod
    def get_health_care_center_by_id(self, center_id: UUID) -> Optional[HealthCareCenterDto]:
        """Get health care center by ID"""
        pass 