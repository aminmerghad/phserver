import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta

from app.services.delivery_service.application.dtos.delivery_dto import (
    DeliveryRoutesResponseDto,
    DeliveryRouteDto,
    DeliveryLocationDto,
    DeliveryOrderDto
)
from app.services.delivery_service.application.queries.get_delivery_routes_query import GetDeliveryRoutesQuery
from app.services.delivery_service.domain.entities.delivery_route_entity import (
    DeliveryRouteEntity,
    DeliveryLocationEntity,
    DeliveryOrderEntity
)
from app.services.delivery_service.domain.enums.delivery_status import DeliveryStatus
from app.services.delivery_service.domain.interfaces.unit_of_work import UnitOfWork

# Configure logger
logger = logging.getLogger(__name__)


class GetDeliveryRoutesUseCase:
    """
    Use case for getting delivery routes from processing orders.
    
    This use case handles:
    1. Getting all orders with PROCESSING status from Order Service
    2. Getting health care center information for each order from Auth Service
    3. Grouping orders by location (health care center)
    4. Creating delivery routes with GPS coordinates
    5. Returning optimized delivery route information
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, query: GetDeliveryRoutesQuery) -> DeliveryRoutesResponseDto:
        """Execute the get delivery routes use case"""
        logger.info("Starting delivery routes generation")
        
        try:
            with self._uow:
                # Step 1: Get prioritized orders from Order Service (SHIPPED first, then PROCESSING)
                prioritized_orders = self._get_prioritized_orders()
                logger.info(f"Found {len(prioritized_orders)} prioritized orders (SHIPPED first, then PROCESSING)")
                
                if not prioritized_orders:
                    return DeliveryRoutesResponseDto(
                        routes=[],
                        total_routes=0,
                        processing_orders_count=0,
                        total_estimated_deliveries=0
                    )
                
                # Step 2: Get health care center information for each order
                enriched_orders = self._enrich_orders_with_location(prioritized_orders)
                logger.info(f"Enriched {len(enriched_orders)} orders with location data")
                
                # Step 3: Group orders by location if requested
                if query.group_by_location:
                    delivery_routes = self._group_orders_by_location(enriched_orders)
                else:
                    delivery_routes = self._create_individual_routes(enriched_orders)
                
                # Step 4: Apply limit if specified
                if query.limit:
                    delivery_routes = delivery_routes[:query.limit]
                
                # Step 5: Create response
                response = self._create_response(delivery_routes, len(prioritized_orders))
                
                logger.info(f"Generated {len(delivery_routes)} delivery routes")
                return response
                
        except Exception as e:
            logger.error(f"Error generating delivery routes: {str(e)}", exc_info=True)
            raise
    
    def _get_prioritized_orders(self) -> List:
        """Get prioritized orders for delivery (SHIPPED first, then PROCESSING)"""
        return self._uow.order_service_port.get_prioritized_orders_for_delivery()
    
    def _enrich_orders_with_location(self, orders) -> List[Dict]:
        """Enrich orders with health care center location information"""
        enriched_orders = []
        
        for order in orders:
            try:
                # Get health care center for this user
                health_care_center = self._uow.auth_service_port.get_user_health_care_center(order.user_id)
                
                if health_care_center:
                    enriched_orders.append({
                        'order': order,
                        'location': health_care_center
                    })
                else:
                    logger.warning(f"No health care center found for user {order.user_id} in order {order.order_id}")
            except Exception as e:
                logger.warning(f"Failed to get health care center for order {order.order_id}: {str(e)}")
        
        return enriched_orders
    
    def _group_orders_by_location(self, enriched_orders) -> List[DeliveryRouteEntity]:
        """Group orders by health care center location"""
        location_groups = defaultdict(list)
        
        # Group orders by health care center ID
        for enriched_order in enriched_orders:
            location = enriched_order['location']
            location_id = location.id
            location_groups[location_id].append(enriched_order)
        
        # Create delivery routes for each location
        delivery_routes = []
        for location_id, orders_group in location_groups.items():
            # Use the first order's location for route location
            location_data = orders_group[0]['location']
            
            # Create location entity
            location_entity = DeliveryLocationEntity(
                health_care_center_id=location_data.id,
                health_care_center_name=location_data.name,
                address=location_data.address,
                latitude=location_data.latitude,
                longitude=location_data.longitude,
                phone=location_data.phone,
                email=location_data.email
            )
            
            # Create order entities
            order_entities = []
            for enriched_order in orders_group:
                order = enriched_order['order']
                order_entity = DeliveryOrderEntity(
                    order_id=order.order_id,
                    user_id=order.user_id,
                    total_amount=order.total_amount,
                    items_count=order.items_count,
                    notes=order.notes,
                    created_at=order.created_at
                )
                order_entities.append(order_entity)
            
            # Create delivery route
            route_entity = DeliveryRouteEntity(
                route_name=f"Route to {location_data.name}",
                orders=order_entities,
                location=location_entity,
                status=DeliveryStatus.PENDING,
                estimated_delivery_time=self._calculate_estimated_delivery_time(),
                created_at=datetime.utcnow()
            )
            
            delivery_routes.append(route_entity)
        
        return delivery_routes
    
    def _create_individual_routes(self, enriched_orders) -> List[DeliveryRouteEntity]:
        """Create individual routes for each order"""
        delivery_routes = []
        
        for enriched_order in enriched_orders:
            order = enriched_order['order']
            location_data = enriched_order['location']
            
            # Create location entity
            location_entity = DeliveryLocationEntity(
                health_care_center_id=location_data.id,
                health_care_center_name=location_data.name,
                address=location_data.address,
                latitude=location_data.latitude,
                longitude=location_data.longitude,
                phone=location_data.phone,
                email=location_data.email
            )
            
            # Create order entity
            order_entity = DeliveryOrderEntity(
                order_id=order.order_id,
                user_id=order.user_id,
                total_amount=order.total_amount,
                items_count=order.items_count,
                notes=order.notes,
                created_at=order.created_at
            )
            
            # Create delivery route
            route_entity = DeliveryRouteEntity(
                route_name=f"Delivery to {location_data.name} - Order #{order.order_id}",
                orders=[order_entity],
                location=location_entity,
                status=DeliveryStatus.PENDING,
                estimated_delivery_time=self._calculate_estimated_delivery_time(),
                created_at=datetime.utcnow()
            )
            
            delivery_routes.append(route_entity)
        
        return delivery_routes
    
    def _calculate_estimated_delivery_time(self) -> datetime:
        """Calculate estimated delivery time (placeholder logic)"""
        # For now, estimate 2 hours from now
        # In a real system, this would consider factors like:
        # - Distance to location
        # - Current traffic conditions
        # - Delivery capacity
        # - Priority of orders
        return datetime.utcnow() + timedelta(hours=2)
    
    def _create_response(self, delivery_routes: List[DeliveryRouteEntity], total_processing_orders: int) -> DeliveryRoutesResponseDto:
        """Create the response DTO from delivery route entities"""
        route_dtos = []
        
        for route_entity in delivery_routes:
            # Convert location entity to DTO
            location_dto = DeliveryLocationDto(
                health_care_center_id=route_entity.location.health_care_center_id,
                health_care_center_name=route_entity.location.health_care_center_name,
                address=route_entity.location.address,
                latitude=route_entity.location.latitude,
                longitude=route_entity.location.longitude,
                phone=route_entity.location.phone,
                email=route_entity.location.email
            ) if route_entity.location else None
            
            # Convert order entities to DTOs
            order_dtos = []
            for order_entity in route_entity.orders:
                order_dto = DeliveryOrderDto(
                    order_id=order_entity.order_id,
                    user_id=order_entity.user_id,
                    total_amount=order_entity.total_amount,
                    items_count=order_entity.items_count,
                    notes=order_entity.notes,
                    created_at=order_entity.created_at
                )
                order_dtos.append(order_dto)
            
            # Create route DTO
            route_dto = DeliveryRouteDto(
                id=route_entity.id,
                route_name=route_entity.route_name,
                orders=order_dtos,
                location=location_dto,
                status=route_entity.status,
                estimated_delivery_time=route_entity.estimated_delivery_time,
                total_amount=route_entity.get_total_amount(),
                total_items_count=route_entity.get_total_items_count(),
                created_at=route_entity.created_at,
                updated_at=route_entity.updated_at
            )
            
            route_dtos.append(route_dto)
        
        # Calculate total estimated deliveries
        total_estimated_deliveries = sum(len(route.orders) for route in route_dtos)
        
        return DeliveryRoutesResponseDto(
            routes=route_dtos,
            total_routes=len(route_dtos),
            processing_orders_count=total_processing_orders,
            total_estimated_deliveries=total_estimated_deliveries
        ) 