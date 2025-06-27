from http import HTTPStatus
from typing import Dict, Any, Tuple
from uuid import UUID

from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from app.apis.base_routes import BaseRoute
from app.apis.delivery.schemas import (
    DeliveryQuerySchema,
    DeliveryRoutesApiResponseSchema,
    ErrorResponseSchema
)
from app.extensions import container
from app.shared.domain.schema.common_errors import ErrorResponseSchema
from app.apis import delivery_bp


@delivery_bp.route('/routes')
class DeliveryRoutesRoute(BaseRoute):
    """Route for getting delivery routes"""
    
    @delivery_bp.doc(
        summary="Get delivery routes", 
        description="Get delivery routes for prioritized orders (SHIPPED first, then PROCESSING) with GPS locations"
    )
    @delivery_bp.arguments(DeliveryQuerySchema, location="query")
    @delivery_bp.response(HTTPStatus.INTERNAL_SERVER_ERROR, ErrorResponseSchema)
    @delivery_bp.response(HTTPStatus.OK, DeliveryRoutesApiResponseSchema)

    @jwt_required()
    def get(self, query_args: Dict[str, Any]) -> Tuple[dict, int]:
        """
        Get delivery routes for prioritized orders.
        
        This endpoint:
        1. Gets prioritized orders (SHIPPED orders first, then PROCESSING orders if no SHIPPED orders exist)
        2. Retrieves health care center GPS coordinates for each order
        3. Groups orders by location and creates optimized delivery routes
        4. Returns routes with GPS coordinates and order details
        """
        try:
            # Get delivery service from container
            delivery_service = container.delivery_service()
            
            # Extract query parameters
            include_location_details = query_args.get('include_location_details', True)
            group_by_location = query_args.get('group_by_location', True)
            limit = query_args.get('limit')
            
            # Get delivery routes
            result = delivery_service.get_delivery_routes(
                include_location_details=include_location_details,
                group_by_location=group_by_location,
                limit=limit
            )
            
            return self._success_response(
                data=result,
                message=f"Retrieved {result['summary']['total_routes']} delivery routes successfully",
                status_code=HTTPStatus.OK
            )
            
        except Exception as e:
            return self._error_response(
                message=f"Failed to get delivery routes: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )


@delivery_bp.route('/routes/location/<uuid:health_care_center_id>')
class DeliveryRouteByLocationRoute(BaseRoute):
    """Route for getting delivery route by specific location"""
    
    @delivery_bp.doc(
        summary="Get delivery route by location", 
        description="Get delivery route for a specific health care center location"
    )
    @delivery_bp.response(HTTPStatus.OK)
    @delivery_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema)
    @delivery_bp.response(HTTPStatus.INTERNAL_SERVER_ERROR, ErrorResponseSchema)
    @jwt_required()
    def get(self, health_care_center_id: UUID) -> Tuple[dict, int]:
        """
        Get delivery route for a specific health care center location.
        
        Args:
            health_care_center_id: ID of the health care center
        """
        try:
            # Get delivery service from container
            delivery_service = container.delivery_service()
            
            # Get delivery route by location
            result = delivery_service.get_delivery_route_by_location(str(health_care_center_id))
            
            if not result.get('route'):
                return self._error_response(
                    message=result.get('message', 'No delivery route found for this location'),
                    status_code=HTTPStatus.NOT_FOUND
                )
            
            return self._success_response(
                data=result,
                message="Delivery route retrieved successfully",
                status_code=HTTPStatus.OK
            )
            
        except Exception as e:
            return self._error_response(
                message=f"Failed to get delivery route by location: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )


@delivery_bp.route('/statistics')
class DeliveryStatisticsRoute(BaseRoute):
    """Route for getting delivery statistics"""
    
    @delivery_bp.doc(
        summary="Get delivery statistics", 
        description="Get delivery statistics and analytics"
    )
    @delivery_bp.response(HTTPStatus.OK)
    @delivery_bp.response(HTTPStatus.INTERNAL_SERVER_ERROR, ErrorResponseSchema)
    @jwt_required()
    def get(self) -> Tuple[dict, int]:
        """
        Get delivery statistics and analytics.
        
        Returns comprehensive statistics about delivery routes, including:
        - Total routes and orders
        - Value distribution
        - Location statistics
        - Status distribution
        """
        try:
            # Get delivery service from container
            delivery_service = container.delivery_service()
            
            # Get delivery statistics
            result = delivery_service.get_delivery_statistics()
            
            return self._success_response(
                data=result,
                message="Delivery statistics retrieved successfully",
                status_code=HTTPStatus.OK
            )
            
        except Exception as e:
            return self._error_response(
                message=f"Failed to get delivery statistics: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            ) 