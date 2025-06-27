import logging
from typing import Dict, Any, List
from uuid import UUID

from app.dataBase import Database
from app.services.delivery_service.application.queries.get_delivery_routes_query import GetDeliveryRoutesQuery
from app.services.delivery_service.application.use_cases.get_delivery_routes import GetDeliveryRoutesUseCase
from app.services.delivery_service.infrastructure.unit_of_work.delivery_unit_of_work import DeliveryUnitOfWork
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

# Configure logger
logger = logging.getLogger(__name__)


class DeliveryService:
    """
    Delivery Service for managing delivery routes and logistics.
    
    This service handles:
    - Getting GPS coordinates from health care centers
    - Retrieving processing orders
    - Simple coordinate-focused delivery information
    """
    
    def __init__(self, db: Database, event_bus: EventBus, acl: UnifiedACL):
        """
        Initialize the delivery service.
        
        Args:
            db: Database instance
            event_bus: Event bus for publishing events
            acl: Unified ACL for inter-service communication
        """
        self._db_session = db.get_session()
        self._event_bus = event_bus
        self._acl = acl
        self._init_resources()
        logger.info("Delivery service initialized")
    
    def _init_resources(self):
        """Initialize internal resources and dependencies"""
        # Initialize Unit of Work
        self._uow = DeliveryUnitOfWork(self._event_bus, self._acl)
        
        # Initialize Use Cases
        self._get_delivery_routes_use_case = GetDeliveryRoutesUseCase(self._uow)
        
        logger.info("Delivery service resources initialized")
    
    def get_gps_coordinates_for_orders(self) -> Dict[str, Any]:
        """
        Get GPS coordinates for prioritized orders.
        Prioritizes SHIPPED orders first, then PROCESSING orders if no SHIPPED orders exist.
        
        Returns:
            Dictionary containing GPS coordinates and order information
        """
        logger.info("Getting GPS coordinates for prioritized orders (SHIPPED first, then PROCESSING)")
        
        try:
            # Step 1: Get prioritized orders (SHIPPED first, then PROCESSING)
            prioritized_orders = self._uow.order_service_port.get_prioritized_orders_for_delivery()
            logger.info(f"Found {len(prioritized_orders)} prioritized orders (SHIPPED first, then PROCESSING)")
            
            if not prioritized_orders:
                return {
                    "success": True,
                    "message": "No prioritized orders found",
                    "orders_with_gps": [],
                    "total_orders": 0,
                    "orders_with_coordinates": 0
                }
            
            # Step 2: Get GPS coordinates for each order
            orders_with_gps = []
            successful_coordinates = 0
            
            for order in prioritized_orders:
                try:
                    # Get health care center for this user
                    health_care_center = self._uow.auth_service_port.get_user_health_care_center(order.user_id)
                    
                    order_info = {
                        "order_id": str(order.order_id),
                        "user_id": str(order.user_id),
                        "total_amount": order.total_amount,
                        "items_count": order.items_count,
                        "status": order.status,
                        "created_at": order.created_at
                    }
                    
                    if health_care_center:
                        order_info["gps_coordinates"] = {
                            "latitude": health_care_center.latitude,
                            "longitude": health_care_center.longitude,
                            "health_care_center": {
                                "id": str(health_care_center.id),
                                "name": health_care_center.name,
                                "address": health_care_center.address,
                                "phone": health_care_center.phone,
                                "email": health_care_center.email
                            }
                        }
                        successful_coordinates += 1
                        logger.info(f"✅ GPS coordinates found for order {order.order_id}: ({health_care_center.latitude}, {health_care_center.longitude})")
                    else:
                        order_info["gps_coordinates"] = None
                        order_info["error"] = "No health care center found for user"
                        logger.warning(f"❌ No GPS coordinates found for order {order.order_id} (user: {order.user_id})")
                    
                    orders_with_gps.append(order_info)
                    
                except Exception as e:
                    logger.error(f"Error getting GPS coordinates for order {order.order_id}: {str(e)}")
                    orders_with_gps.append({
                        "order_id": str(order.order_id),
                        "user_id": str(order.user_id),
                        "gps_coordinates": None,
                        "error": f"Error retrieving coordinates: {str(e)}"
                    })
            
            result = {
                "success": True,
                "message": f"Retrieved GPS coordinates for {successful_coordinates}/{len(prioritized_orders)} orders",
                "orders_with_gps": orders_with_gps,
                "total_orders": len(prioritized_orders),
                "orders_with_coordinates": successful_coordinates,
                "orders_without_coordinates": len(prioritized_orders) - successful_coordinates
            }
            
            logger.info(f"GPS coordinate retrieval completed: {successful_coordinates}/{len(prioritized_orders)} successful")
            return result
            
        except Exception as e:
            logger.error(f"Error getting GPS coordinates: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "orders_with_gps": [],
                "total_orders": 0,
                "orders_with_coordinates": 0
            }
    
    def get_delivery_routes(self, include_location_details: bool = True, 
                          group_by_location: bool = False, 
                          limit: int = None) -> Dict[str, Any]:
        """
        Get delivery routes for prioritized orders.
        Prioritizes SHIPPED orders first, then PROCESSING orders if no SHIPPED orders exist.
        
        Args:
            include_location_details: Whether to include detailed location information
            group_by_location: Whether to group orders by health care center location
            limit: Maximum number of routes to return
            
        Returns:
            Dictionary containing delivery routes with the correct structure for the API
        """
        logger.info(f"Getting delivery routes with GPS coordinates (limit={limit})")
        
        try:
            # Get GPS coordinates data
            gps_data = self.get_gps_coordinates_for_orders()
            
            if not gps_data["success"]:
                return {
                    "routes": [],
                    "summary": {
                        "total_routes": 0,
                        "processing_orders_count": 0,
                        "total_estimated_deliveries": 0
                    }
                }
            
            # Transform the GPS data into the expected route structure
            routes = []
            orders_with_coords = [order for order in gps_data["orders_with_gps"] if order.get("gps_coordinates")]
            
            if group_by_location:
                # Group orders by health care center
                location_groups = {}
                for order in orders_with_coords:
                    center_id = order["gps_coordinates"]["health_care_center"]["id"]
                    if center_id not in location_groups:
                        location_groups[center_id] = []
                    location_groups[center_id].append(order)
                
                # Create routes for each location group
                for center_id, orders_group in location_groups.items():
                    first_order = orders_group[0]
                    center_info = first_order["gps_coordinates"]["health_care_center"]
                    coords = first_order["gps_coordinates"]
                    
                    route = {
                        "id": None,
                        "route_name": f"Route to {center_info['name']}",
                        "status": "PENDING",
                        "estimated_delivery_time": None,
                        "total_amount": sum(order.get("total_amount", 0) for order in orders_group),
                        "total_items_count": sum(order.get("items_count", 0) for order in orders_group),
                        "created_at": None,
                        "updated_at": None,
                        "location": {
                            "health_care_center_id": center_info["id"],
                            "health_care_center_name": center_info["name"],
                            "address": center_info["address"],
                            "latitude": coords["latitude"],
                            "longitude": coords["longitude"],
                            "phone": center_info.get("phone"),
                            "email": center_info.get("email")
                        },
                        "orders": []
                    }
                    
                    # Add orders to the route
                    for order in orders_group:
                        route_order = {
                            "order_id": order["order_id"],
                            "user_id": order["user_id"],
                            "total_amount": order.get("total_amount", 0),
                            "items_count": order.get("items_count", 0),
                            "notes": None,
                            "created_at": order.get("created_at")
                        }
                        route["orders"].append(route_order)
                    
                    routes.append(route)
            else:
                # Create individual routes for each order
                for order in orders_with_coords:
                    center_info = order["gps_coordinates"]["health_care_center"]
                    coords = order["gps_coordinates"]
                    
                    route = {
                        "id": None,
                        "route_name": f"Delivery to {center_info['name']} - Order #{order['order_id'][:8]}",
                        "status": "PENDING",
                        "estimated_delivery_time": None,
                        "total_amount": order.get("total_amount", 0),
                        "total_items_count": order.get("items_count", 0),
                        "created_at": None,
                        "updated_at": None,
                        "location": {
                            "health_care_center_id": center_info["id"],
                            "health_care_center_name": center_info["name"],
                            "address": center_info["address"],
                            "latitude": coords["latitude"],
                            "longitude": coords["longitude"],
                            "phone": center_info.get("phone"),
                            "email": center_info.get("email")
                        },
                        "orders": [{
                            "order_id": order["order_id"],
                            "user_id": order["user_id"],
                            "total_amount": order.get("total_amount", 0),
                            "items_count": order.get("items_count", 0),
                            "notes": None,
                            "created_at": order.get("created_at")
                        }]
                    }
                    routes.append(route)
            
            # Apply limit if specified
            if limit and len(routes) > limit:
                routes = routes[:limit]
            
            # Calculate summary
            total_estimated_deliveries = sum(len(route["orders"]) for route in routes)
            
            result = {
                "routes": routes,
                "summary": {
                    "total_routes": len(routes),
                    "processing_orders_count": gps_data["total_orders"],
                    "total_estimated_deliveries": total_estimated_deliveries
                }
            }
            
            logger.info(f"Successfully created {len(routes)} delivery routes")
            return result
            
        except Exception as e:
            logger.error(f"Error getting delivery routes: {str(e)}", exc_info=True)
            return {
                "routes": [],
                "summary": {
                    "total_routes": 0,
                    "processing_orders_count": 0,
                    "total_estimated_deliveries": 0
                }
            }
    
    def get_delivery_route_by_location(self, health_care_center_id: str) -> Dict[str, Any]:
        """
        Get delivery route for a specific health care center location.
        
        Args:
            health_care_center_id: ID of the health care center
            
        Returns:
            Dictionary containing delivery route information for the specific location
        """
        logger.info(f"Getting delivery route for health care center: {health_care_center_id}")
        
        try:
            # Get all orders with GPS coordinates
            all_orders = self.get_gps_coordinates_for_orders()
            
            if not all_orders["success"]:
                return all_orders
            
            # Filter orders for the specified health care center
            matching_orders = []
            for order in all_orders["orders_with_gps"]:
                if (order.get("gps_coordinates") and 
                    order["gps_coordinates"]["health_care_center"]["id"] == health_care_center_id):
                    matching_orders.append(order)
            
            return {
                "success": True,
                "health_care_center_id": health_care_center_id,
                "orders": matching_orders,
                "total_orders": len(matching_orders),
                "message": f"Found {len(matching_orders)} orders for health care center {health_care_center_id}"
            }
            
        except Exception as e:
            logger.error(f"Error getting delivery route by location: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "orders": []
            }
    
    def get_delivery_statistics(self) -> Dict[str, Any]:
        """
        Get delivery statistics and analytics.
        
        Returns:
            Dictionary containing delivery statistics
        """
        logger.info("Getting delivery statistics")
        
        try:
            # Get GPS coordinates data
            gps_data = self.get_gps_coordinates_for_orders()
            
            if not gps_data["success"]:
                return gps_data
            
            # Calculate statistics
            orders = gps_data["orders_with_gps"]
            total_value = sum(order.get("total_amount", 0) for order in orders if order.get("total_amount"))
            
            # Group by health care center
            centers = {}
            for order in orders:
                if order.get("gps_coordinates"):
                    center_id = order["gps_coordinates"]["health_care_center"]["id"]
                    center_name = order["gps_coordinates"]["health_care_center"]["name"]
                    
                    if center_id not in centers:
                        centers[center_id] = {
                            "name": center_name,
                            "orders_count": 0,
                            "total_value": 0,
                            "coordinates": {
                                "latitude": order["gps_coordinates"]["latitude"],
                                "longitude": order["gps_coordinates"]["longitude"]
                            }
                        }
                    
                    centers[center_id]["orders_count"] += 1
                    centers[center_id]["total_value"] += order.get("total_amount", 0)
            
            statistics = {
                "success": True,
                "total_orders": gps_data["total_orders"],
                "orders_with_coordinates": gps_data["orders_with_coordinates"],
                "orders_without_coordinates": gps_data["orders_without_coordinates"],
                "total_value": total_value,
                "health_care_centers_count": len(centers),
                "health_care_centers": list(centers.values()),
                "coordinate_success_rate": (
                    gps_data["orders_with_coordinates"] / gps_data["total_orders"] * 100
                    if gps_data["total_orders"] > 0 else 0
                )
            }
            
            logger.info("Successfully calculated delivery statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting delivery statistics: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            } 