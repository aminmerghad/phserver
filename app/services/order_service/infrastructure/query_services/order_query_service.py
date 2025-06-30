from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session, joinedload
# from functools import lru_cache

from app.services.order_service.application.dtos.order_dto import (
    OrderDTO,
    OrderFilterPaginationDTO,
    OrderFilterResponseDTO,
    OrderItemDTO,
    OrderSummaryDTO,
    OrderFilterDTO
)
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.infrastructure.persistence.mappers.order_mapper import OrderMapper
from app.services.order_service.infrastructure.persistence.models.order import OrderModel, OrderItemModel
from app.shared.acl.unified_acl import UnifiedACL

class OrderQueryService:
    def __init__(self, session: Session, acl: UnifiedACL = None):
        self._session = session
        self._mapper = OrderMapper()
        self._acl = acl
        # self._cache = {}  # Simple in-memory cache
        # self._cache_ttl = 300  # 5 minutes in seconds

    def _get_product_name(self, product_id: UUID) -> str:
        """
        Get product name from product service via ACL.
        Falls back to a default name if product service is unavailable.
        """
        if not self._acl:
            return f"Product {str(product_id).split('-')[0]}"
            
        try:
            from app.services.order_service.infrastructure.adapters.outgoing.product_adapter import ProductServiceAdapter
            product_adapter = ProductServiceAdapter(self._acl)
            product = product_adapter.get_product_by_id(product_id)
            
            if product and 'name' in product:
                return product['name']
            else:
                return f"Product {str(product_id).split('-')[0]}"
                
        except Exception as e:
            # Log the error but don't break the order query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch product name for {product_id}: {str(e)}")
            return f"Product {str(product_id).split('-')[0]}"

    def _get_product_names_batch(self, product_ids: List[UUID]) -> Dict[UUID, str]:
        """
        Get product names in batch for better performance.
        Falls back to default names if product service is unavailable.
        """
        product_names = {}
        
        if not self._acl or not product_ids:
            # Return default names if ACL is not available or no product IDs
            return {pid: f"Product {str(pid).split('-')[0]}" for pid in product_ids}
            
        try:
            from app.services.order_service.infrastructure.adapters.outgoing.product_adapter import ProductServiceAdapter
            product_adapter = ProductServiceAdapter(self._acl)
            
            for product_id in product_ids:
                try:
                    product = product_adapter.get_product_by_id(product_id)
                    if product and 'name' in product:
                        product_names[product_id] = product['name']
                    else:
                        product_names[product_id] = f"Product {str(product_id).split('-')[0]}"
                except Exception:
                    product_names[product_id] = f"Product {str(product_id).split('-')[0]}"
            
        except Exception as e:
            # Log the error but don't break the order query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch product names in batch: {str(e)}")
            # Return default names
            product_names = {pid: f"Product {str(pid).split('-')[0]}" for pid in product_ids}
            
        return product_names

    def _get_user_name(self, user_id: UUID) -> str:
        """
        Get user name from auth service via ACL.
        Falls back to a default name if auth service is unavailable.
        """
        if not self._acl or not user_id:
            return f"User {str(user_id).split('-')[0]}" if user_id else "Unknown User"
            
        try:
            from app.services.order_service.infrastructure.adapters.outgoing.auth_adapter import AuthServiceAdapter
            auth_adapter = AuthServiceAdapter(self._acl)
            user = auth_adapter.get_user_by_id(user_id)
            
            if user and 'full_name' in user:
                return user['full_name']
            else:
                return f"User {str(user_id).split('-')[0]}"
                
        except Exception as e:
            # Log the error but don't break the order query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch user name for {user_id}: {str(e)}")
            return f"User {str(user_id).split('-')[0]}"

    def _get_user_names_batch(self, user_ids: List[UUID]) -> Dict[UUID, str]:
        """
        Get user names in batch for better performance.
        Falls back to default names if auth service is unavailable.
        """
        user_names = {}
        
        if not self._acl or not user_ids:
            # Return default names if ACL is not available or no user IDs
            return {uid: f"User {str(uid).split('-')[0]}" for uid in user_ids}
            
        try:
            from app.services.order_service.infrastructure.adapters.outgoing.auth_adapter import AuthServiceAdapter
            auth_adapter = AuthServiceAdapter(self._acl)
            
            for user_id in user_ids:
                try:
                    user = auth_adapter.get_user_by_id(user_id)
                    if user and 'full_name' in user:
                        user_names[user_id] = user['full_name']
                    else:
                        user_names[user_id] = f"User {str(user_id).split('-')[0]}"
                except Exception:
                    user_names[user_id] = f"User {str(user_id).split('-')[0]}"
                    
        except Exception as e:
            # Log the error but don't break the order query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch user names in batch: {str(e)}")
            # Return default names
            user_names = {uid: f"User {str(uid).split('-')[0]}" for uid in user_ids}
            
        return user_names

    def _get_health_center_name(self, user_id: UUID) -> str:
        """Get health center name for a user"""
        if not user_id or not self._acl:
            return None
            
        try:
            from app.services.order_service.infrastructure.adapters.outgoing.auth_adapter import AuthServiceAdapter
            auth_adapter = AuthServiceAdapter(self._acl)
            
            # First get the user to find their health_care_center_id
            user = auth_adapter.get_user_by_id(user_id)
            if not user or not user.get('health_care_center_id'):
                return None
                
            # Then get the health center details
            health_care_center_id = user.get('health_care_center_id')
            center = auth_adapter.get_health_care_center_by_id(UUID(health_care_center_id))
            if center and center.get('name'):
                return center['name']
            else:
                return None
                
        except Exception as e:
            # Log error but don't fail the query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error fetching health center for user {user_id}: {str(e)}")
            return None

    def _get_health_center_names_batch(self, user_ids: List[UUID]) -> Dict[UUID, str]:
        """Get health center names for multiple users in a single batch operation"""
        if not user_ids or not self._acl:
            return {}
            
        health_center_names = {}
        
        try:
            from app.services.order_service.infrastructure.adapters.outgoing.auth_adapter import AuthServiceAdapter
            auth_adapter = AuthServiceAdapter(self._acl)
            
            # Get all users by IDs first to get their health_care_center_ids
            users_data = {}
            for user_id in user_ids:
                try:
                    user = auth_adapter.get_user_by_id(user_id)
                    if user:
                        users_data[user_id] = user
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error fetching user {user_id}: {str(e)}")
                    continue
            
            # Get unique health center IDs
            center_ids = set()
            for user_data in users_data.values():
                if user_data.get('health_care_center_id'):
                    center_ids.add(UUID(user_data['health_care_center_id']))
            
            # Fetch health center details for all unique center IDs
            centers_data = {}
            for center_id in center_ids:
                try:
                    center = auth_adapter.get_health_care_center_by_id(center_id)
                    if center:
                        centers_data[center_id] = center
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error fetching health center {center_id}: {str(e)}")
                    continue
            
            # Map user IDs to health center names
            for user_id, user_data in users_data.items():
                if user_data.get('health_care_center_id'):
                    center_id = UUID(user_data['health_care_center_id'])
                    center_data = centers_data.get(center_id)
                    if center_data and center_data.get('name'):
                        health_center_names[user_id] = center_data['name']
                        
        except Exception as e:
            # If batch operation fails, return empty dict
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error in batch health center fetch: {str(e)}")
            
        return health_center_names

    def get_order_by_id(self, order_id: UUID) -> Optional[OrderModel]:
        """Get order details by ID with eager loading of items"""
        try:
            order = self._session.query(OrderModel).options(
                joinedload(OrderModel.items)  # Eager load items
            ).filter(
                OrderModel.id == order_id
            ).first()
            
            if order:
                # Check for encoding issues in text fields
                try:
                    # Test accessing each field that could have encoding issues
                    _ = str(order.id)
                    _ = str(order.user_id) if order.user_id else None
                    _ = str(order.status)
                    _ = float(order.total_amount) if order.total_amount else 0
                    
                    # Check notes field - this is likely where the encoding issue is
                    if order.notes:
                        # Try to encode/decode to detect issues
                        notes_safe = order.notes.encode('utf-8', errors='ignore').decode('utf-8')
                        if notes_safe != order.notes:
                            # There was corrupted data, log and clean it
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Found corrupted UTF-8 data in order {order_id} notes field. Cleaning...")
                            # You could update the database here if needed
                            order.notes = notes_safe
                    
                    # Check items for encoding issues
                    for item in order.items:
                        _ = str(item.id)
                        _ = str(item.product_id)
                        _ = int(item.quantity)
                        _ = float(item.price)
                        
                except UnicodeDecodeError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"UTF-8 encoding error in order {order_id}: {str(e)}")
                    # Try to clean the data or return None
                    return None
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing order {order_id} data: {str(e)}")
                    return None
            
            return order
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database error fetching order {order_id}: {str(e)}")
            return None

    def get_orders_by_user_id(self, user_id: UUID, page: int = 1, per_page: int = 10) -> List[OrderModel]:
        """Get all orders for a specific user ordered by creation date (newest first)"""
        # cache_key = f"user_orders_{user_id}_{page}_{per_page}"
        # cached_result = self._get_from_cache(cache_key)
        
        # if cached_result:
        #     return cached_result
        orders = self._session.query(OrderModel).options(
            joinedload(OrderModel.items)
        ).filter(
            OrderModel.user_id == user_id
        ).order_by(
            desc(OrderModel.created_at)
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        # Get user name for this specific user
        user_name = self._get_user_name(user_id)
        health_center_name = self._get_health_center_name(user_id)
        
        # Convert to DTOs with user name and health center name
        result = []
        for order in orders:
            # Get all product IDs from the order items
            product_ids = [item.product_id for item in order.items] if order.items else []
            
            # Fetch product names in batch for better performance
            product_names = self._get_product_names_batch(product_ids)
                
            result.append(OrderSummaryDTO(
                order_id=order.id,
                consumer_id=order.user_id,
                status=order.status,
                total_amount=order.total_amount,
                items_count=len(order.items) if order.items else 0,
                created_at=order.created_at,
                items=[{
                    'id': item.id,
                    'product_id': item.product_id,
                    'name': product_names.get(item.product_id, f"Product {str(item.product_id).split('-')[0]}"),  # Use actual product name
                    'quantity': item.quantity,
                    'price': item.price,
                    'total_price': item.quantity*item.price
                } for item in order.items],
                consumer_name=user_name,
                health_center_name=health_center_name
            ))
        
        # self._add_to_cache(cache_key, orders)
        return OrderFilterResponseDTO(
            orders=result,
            pagination=OrderFilterPaginationDTO(
                total=len(orders),
                page=page,
                pages=1,
                per_page=per_page,
            )
        )

    def get_orders_by_filter(
        self,
        filter_dto: Optional[OrderFilterDTO] = None,
    ) -> OrderFilterResponseDTO:
        """Get filtered and paginated orders"""
        # Build cache key based on filter parameters
        # cache_params = "_".join([
        #     f"{k}:{v}" for k, v in filter_dto.__dict__.items() if v is not None
        # ])
        # cache_key = f"filtered_orders_{cache_params}"
        # cached_result = self._get_from_cache(cache_key)
        
        # if cached_result:
        #     return cached_result
        
        # Build base query
        query = self._session.query(OrderModel).options(
            joinedload(OrderModel.items)
        ).order_by(desc(OrderModel.created_at))

        # Apply filters
        if filter_dto.user_id:
            query = query.filter(OrderModel.user_id == filter_dto.user_id)
        if filter_dto.status:
            query = query.filter(OrderModel.status == OrderStatus(filter_dto.status))
        if filter_dto.start_date:
            query = query.filter(OrderModel.created_at >= filter_dto.start_date)
        if filter_dto.end_date:
            query = query.filter(OrderModel.created_at <= filter_dto.end_date)
        if filter_dto.min_amount:
            query = query.filter(OrderModel.total_amount >= filter_dto.min_amount)
        if filter_dto.max_amount:
            query = query.filter(OrderModel.total_amount <= filter_dto.max_amount)

        # Get total count for pagination info
        total = query.count()
        pages = (total + filter_dto.per_page - 1) // filter_dto.per_page

        # Apply pagination
        orders = query.order_by(desc(OrderModel.created_at)) \
            .offset((filter_dto.page - 1) * filter_dto.per_page) \
            .limit(filter_dto.per_page) \
            .all()

        # Get all unique user IDs for batch processing
        user_ids = list(set([order.user_id for order in orders if order.user_id]))
        user_names = self._get_user_names_batch(user_ids)
        health_center_names = self._get_health_center_names_batch(user_ids)

        # Convert to DTOs with batch-fetched user names and health center names
        result = []
        for order in orders:
            # Get all product IDs from the order items
            product_ids = [item.product_id for item in order.items] if order.items else []
            
            # Fetch product names in batch for better performance
            product_names = self._get_product_names_batch(product_ids)
            
            # Get consumer name and health center name from batch-fetched data
            consumer_name = user_names.get(order.user_id) if order.user_id else None
            health_center_name = health_center_names.get(order.user_id) if order.user_id else None
                
            result.append(OrderSummaryDTO(
                order_id=order.id,
                consumer_id=order.user_id,
                status=order.status,
                total_amount=order.total_amount,
                items_count=len(order.items) if order.items else 0,
                created_at=order.created_at,
                items=[{
                    'id': item.id,
                    'product_id': item.product_id,
                    'name': product_names.get(item.product_id, f"Product {str(item.product_id).split('-')[0]}"),  # Use actual product name
                    'quantity': item.quantity,
                    'price': item.price,
                    'total_price': item.quantity*item.price
                } for item in order.items],
                consumer_name=consumer_name,
                health_center_name=health_center_name
            ))

        # self._add_to_cache(cache_key, result)
        return OrderFilterResponseDTO(
            orders=result,
            pagination=OrderFilterPaginationDTO(
                total=total,
                page=filter_dto.page,
                pages=pages,
                per_page=filter_dto.per_page,
            )
        )

    # @lru_cache(maxsize=128)
    def get_user_order_stats(self, user_id: UUID) -> dict:
        """Get order statistics for a user (cached with LRU cache for better performance)"""
        stats = self._session.query(
            func.count(OrderModel.id).label('total_orders'),
            func.sum(OrderModel.total_amount).label('total_spent'),
            func.avg(OrderModel.total_amount).label('average_order_value')
        ).filter(
            OrderModel.user_id == user_id
        ).first()

        status_counts = dict(
            self._session.query(
                OrderModel.status,
                func.count(OrderModel.id)
            ).filter(
                OrderModel.user_id == user_id
            ).group_by(OrderModel.status).all()
        )

        return {
            'total_orders': stats.total_orders or 0,
            'total_spent': float(stats.total_spent or 0),
            'average_order_value': float(stats.average_order_value or 0),
            'status_counts': status_counts
        }

    def get_order_history(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[OrderSummaryDTO]:
        """Get recent order history for a user"""
        # cache_key = f"order_history_{user_id}_{limit}"
        # cached_result = self._get_from_cache(cache_key)
        
        # if cached_result:
        #     return cached_result
            
        orders = self._session.query(OrderModel).options(
            joinedload(OrderModel.items)
        ).filter(
            OrderModel.user_id == user_id
        ).order_by(
            desc(OrderModel.created_at)
        ).limit(limit).all()

        # Get user name for this specific user
        user_name = self._get_user_name(user_id)
        health_center_name = self._get_health_center_name(user_id)
        
        # Convert to DTOs with user name and health center name
        result = []
        for order in orders:
            # Get all product IDs from the order items
            product_ids = [item.product_id for item in order.items] if order.items else []
            
            # Fetch product names in batch for better performance
            product_names = self._get_product_names_batch(product_ids)
                
            result.append(OrderSummaryDTO(
                order_id=order.id,
                consumer_id=order.user_id,
                status=order.status,
                total_amount=order.total_amount,
                items_count=len(order.items) if order.items else 0,
                created_at=order.created_at,
                items=[{
                    'id': item.id,
                    'product_id': item.product_id,
                    'name': product_names.get(item.product_id, f"Product {str(item.product_id).split('-')[0]}"),  # Use actual product name
                    'quantity': item.quantity,
                    'price': item.price,
                    'total_price': item.quantity*item.price
                } for item in order.items],
                consumer_name=user_name,
                health_center_name=health_center_name
            ))

        # self._add_to_cache(cache_key, result)
        return result

    def _to_dto(self, model: OrderModel) -> OrderDTO:
        """Convert OrderModel to OrderDTO"""
        if not model:
            return None
            
        entity = self._mapper.to_entity(model)
        
        # Get all product IDs from the order items
        product_ids = [item.product_id for item in entity.items]
        
        # Fetch product names in batch for better performance
        product_names = self._get_product_names_batch(product_ids)
        
        # Fetch consumer name and health center name
        consumer_name = self._get_user_name(entity.user_id) if entity.user_id else None
        health_center_name = self._get_health_center_name(entity.user_id) if entity.user_id else None
        
        return OrderDTO(
            order_id=entity.id,
            user_id=entity.user_id,
            status=entity.status.value,  # Convert OrderStatus enum to string
            total_amount=entity.total_amount,  # Now it's already a Decimal
            items=[{
                'id': str(item.id) if item.id else None,
                'product_id': str(item.product_id),
                'name': product_names.get(item.product_id, f"Product {str(item.product_id).split('-')[0]}"),  # Use actual product name
                'quantity': item.quantity,
                'price': float(item.price.amount),
                'total_price': float(item.total_price.amount)
            } for item in entity.items],
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            completed_at=entity.completed_at,
            consumer_name=consumer_name,
            health_center_name=health_center_name
        )
    

    def _to_summary_dto(self, model: OrderModel) -> OrderSummaryDTO:
        """Convert OrderModel to OrderSummaryDTO"""
        if not model:
            return None
        
        # Get all product IDs from the order items
        product_ids = [item.product_id for item in model.items] if model.items else []
        
        # Fetch product names in batch for better performance
        product_names = self._get_product_names_batch(product_ids)
        
        # Fetch consumer name and health center name
        consumer_name = self._get_user_name(model.user_id) if model.user_id else None
        health_center_name = self._get_health_center_name(model.user_id) if model.user_id else None
            
        return OrderSummaryDTO(
            order_id=model.id,
            consumer_id=model.user_id,
            status=model.status,
            total_amount=model.total_amount,
            items_count=len(model.items) if model.items else 0,
            created_at=model.created_at,
            items=[{
                'id': item.id,
                'product_id': item.product_id,
                'name': product_names.get(item.product_id, f"Product {str(item.product_id).split('-')[0]}"),  # Use actual product name
                'quantity': item.quantity,
                'price': item.price,
                'total_price': item.quantity*item.price
            } for item in model.items],
            consumer_name=consumer_name,
            health_center_name=health_center_name
        )
        
    def _get_from_cache(self, key: str) -> Any:
        """Get value from cache if it exists and is not expired"""
        if key in self._cache:
            cache_entry = self._cache[key]
            if datetime.now().timestamp() - cache_entry['timestamp'] < self._cache_ttl:
                return cache_entry['data']
            else:
                # Remove expired entry
                del self._cache[key]
        return None
        
    def _add_to_cache(self, key: str, data: Any) -> None:
        """Add value to cache with current timestamp"""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }
        
        # Cache cleanup - remove oldest entries if cache is too large
        if len(self._cache) > 1000:  # Arbitrary limit
            # Sort by timestamp and keep newest 800
            sorted_cache = sorted(
                self._cache.items(), 
                key=lambda x: x[1]['timestamp'],
                reverse=True
            )
            self._cache = dict(sorted_cache[:800])
    
    def invalidate_cache(self, key_pattern: str = None) -> None:
        """Invalidate cache entries matching the pattern or all if pattern is None"""
        if key_pattern:
            keys_to_delete = [k for k in self._cache.keys() if key_pattern in k]
            for key in keys_to_delete:
                if key in self._cache:
                    del self._cache[key]
        else:
            self._cache.clear()
    
    # def search_orders(
    #     self,
    #     query: str,
    #     status: Optional[OrderStatus] = None,
    #     page: int = 1,
    #     per_page: int = 10
    # ) -> List[OrderSummaryDTO]:
    #     """Search orders by ID, user ID, or notes with pagination"""
    #     # We don't cache search results as they're likely to change frequently
        
    #     db_query = self._session.query(OrderModel).options(
    #         joinedload(OrderModel.items)
    #     ).filter(
    #         or_(
    #             OrderModel.id.ilike(f"%{query}%"),
    #             OrderModel.user_id.ilike(f"%{query}%"),
    #             OrderModel.notes.ilike(f"%{query}%")
    #         )
    #     )

    #     if status:
    #         db_query = db_query.filter(OrderModel.status == status)

    #     orders = db_query.order_by(desc(OrderModel.created_at))\
    #             .offset((page - 1) * per_page)\
    #             .limit(per_page)\
    #             .all()
                
    #     return [self._to_summary_dto(order) for order in orders]
        

            

    
