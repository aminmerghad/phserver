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

class OrderQueryService:
    def __init__(self, session: Session):
        self._session = session
        self._mapper = OrderMapper()
        # self._cache = {}  # Simple in-memory cache
        # self._cache_ttl = 300  # 5 minutes in seconds

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
        result = [self._to_summary_dto(order) for order in orders]
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

        result = [self._to_summary_dto(order) for order in orders]
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

        result = [self._to_summary_dto(order) for order in orders]
        # self._add_to_cache(cache_key, result)
        return result

    def _to_dto(self, model: OrderModel) -> OrderDTO:
        """Convert OrderModel to OrderDTO"""
        if not model:
            return None
            
        entity = self._mapper.to_entity(model)
        return OrderDTO(
            order_id=entity.id,
            user_id=entity.user_id,
            status=entity.status.value,  # Convert OrderStatus enum to string
            total_amount=entity.total_amount,  # Now it's already a Decimal
            items=[{
                'id': str(item.id) if item.id else None,
                'product_id': str(item.product_id),
                'name': f"Product {str(item.product_id).split('-')[0]}",  # Use a default name since OrderItem doesn't have name
                'quantity': item.quantity,
                'price': float(item.price.amount),
                'total_price': float(item.total_price.amount)
            } for item in entity.items],
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            completed_at=entity.completed_at
        )
    

    def _to_summary_dto(self, model: OrderModel) -> OrderSummaryDTO:
        """Convert OrderModel to OrderSummaryDTO"""
        if not model:
            return None
            
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
                'name': f"Product {str(item.product_id).split('-')[0]}",  # Use a default name since OrderItem doesn't have name
                'quantity': item.quantity,
                'price': item.price,
                'total_price': item.quantity*item.price
            } for item in model.items]
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
        

            

    
