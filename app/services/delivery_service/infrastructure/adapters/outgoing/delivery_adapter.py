from typing import List, Optional
from uuid import UUID

from app.services.delivery_service.application.dtos.delivery_dto import ProcessingOrderDto, PrioritizedOrderDto, HealthCareCenterDto
from app.services.delivery_service.domain.ports.outgoing_ports import OrderServicePort, AuthServicePort
from app.services.delivery_service.domain.requests.get_processing_orders_request import GetProcessingOrdersRequest
from app.services.delivery_service.domain.requests.get_health_care_center_request import (
    GetHealthCareCenterRequest,
    GetUserHealthCareCenterRequest
)
from app.shared.acl.unified_acl import ServiceContext, UnifiedACL
from app.shared.domain.enums.enums import ServiceType


class DeliveryOrderServiceAdapter(OrderServicePort):
    """Adapter for communicating with Order Service via ACL"""
    
    def __init__(self, acl: UnifiedACL):
        self._acl = acl

    def get_processing_orders(self) -> List[ProcessingOrderDto]:
        """Get all orders with PROCESSING status from Order Service"""
        request = GetProcessingOrdersRequest()
        
        result = self._acl.execute_service_operation(
            ServiceContext(
                service_type=ServiceType.ORDER,
                operation="GET_PROCESSING_ORDERS",
                data=request
            )
        )
        
        if not result.success:
            return []
            
        # Transform the response to ProcessingOrderDto list
        orders = []
        for order_data in result.data.get('orders', []):
            orders.append(ProcessingOrderDto(
                order_id=UUID(order_data['id']),
                user_id=UUID(order_data['user_id']),
                status=order_data['status'],
                total_amount=float(order_data['total_amount']),
                items_count=len(order_data.get('items', [])),
                notes=order_data.get('notes'),
                created_at=order_data.get('created_at')
            ))
        
        return orders

    def get_prioritized_orders_for_delivery(self) -> List[PrioritizedOrderDto]:
        """Get prioritized orders for delivery (SHIPPED first, then PROCESSING) from Order Service"""
        # Create a request object (can be empty as the logic is in the service)
        request = GetProcessingOrdersRequest()  # Reusing this for now, could create specific request
        
        result = self._acl.execute_service_operation(
            ServiceContext(
                service_type=ServiceType.ORDER,
                operation="GET_PRIORITIZED_ORDERS_FOR_DELIVERY",
                data=request
            )
        )
        
        if not result.success:
            return []
            
        # Transform the response to PrioritizedOrderDto list
        orders = []
        for order_data in result.data.get('orders', []):
            orders.append(PrioritizedOrderDto(
                order_id=UUID(order_data['id']),
                user_id=UUID(order_data['user_id']),
                status=order_data['status'],
                total_amount=float(order_data['total_amount']),
                items_count=len(order_data.get('items', [])),
                priority=order_data.get('priority', 'NORMAL'),
                notes=order_data.get('notes'),
                created_at=order_data.get('created_at')
            ))
        
        return orders


class DeliveryAuthServiceAdapter(AuthServicePort):
    """Adapter for communicating with Auth Service via ACL"""
    
    def __init__(self, acl: UnifiedACL):
        self._acl = acl

    def get_user_health_care_center(self, user_id: UUID) -> Optional[HealthCareCenterDto]:
        """Get health care center for a user from Auth Service"""
        request = GetUserHealthCareCenterRequest(user_id=user_id)
        
        result = self._acl.execute_service_operation(
            ServiceContext(
                service_type=ServiceType.AUTH,
                operation="GET_USER_HEALTH_CARE_CENTER",
                data=request
            )
        )
        
        if not result.success or not result.data:
            return None
            
        center_data = result.data
        return HealthCareCenterDto(
            id=UUID(center_data['id']),
            name=center_data['name'],
            address=center_data['address'],
            phone=center_data['phone'],
            email=center_data['email'],
            latitude=float(center_data['latitude']),
            longitude=float(center_data['longitude']),
            is_active=center_data.get('is_active', True)
        )

    def get_health_care_center_by_id(self, center_id: UUID) -> Optional[HealthCareCenterDto]:
        """Get health care center by ID from Auth Service"""
        request = GetHealthCareCenterRequest(center_id=center_id)
        
        result = self._acl.execute_service_operation(
            ServiceContext(
                service_type=ServiceType.AUTH,
                operation="GET_HEALTH_CARE_CENTER_BY_ID",
                data=request
            )
        )
        
        if not result.success or not result.data:
            return None
            
        center_data = result.data
        return HealthCareCenterDto(
            id=UUID(center_data['id']),
            name=center_data['name'],
            address=center_data['address'],
            phone=center_data['phone'],
            email=center_data['email'],
            latitude=float(center_data['latitude']),
            longitude=float(center_data['longitude']),
            is_active=center_data.get('is_active', True)
        ) 