from typing import Dict, Any, Optional
from uuid import UUID

from app.shared.acl.unified_acl import UnifiedACL, ServiceContext
from app.shared.domain.enums.enums import ServiceType


class ProductServiceAdapter:
    """
    Adapter for communicating with the product service from the order service.
    """
    
    def __init__(self, acl: UnifiedACL):
        self._acl = acl

    def get_product_by_id(self, product_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get product information by ID from the product service.
        
        Args:
            product_id: The UUID of the product to fetch
            
        Returns:
            Product information as a dictionary, or None if not found
        """
        try:
            result = self._acl.execute_service_operation(
                ServiceContext(
                    service_type=ServiceType.PRODUCT,
                    operation="GET_PRODUCT",
                    data={"product_id": str(product_id)}
                )
            )
            
            if result.success and result.data:
                return result.data
            else:
                return None
                
        except Exception as e:
            # Log the error but don't raise to avoid breaking order queries
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch product {product_id} from product service: {str(e)}")
            return None

    def get_products_by_ids(self, product_ids: list[UUID]) -> Dict[UUID, Dict[str, Any]]:
        """
        Get multiple products by their IDs.
        
        Args:
            product_ids: List of product UUIDs to fetch
            
        Returns:
            Dictionary mapping product_id to product information
        """
        products = {}
        
        for product_id in product_ids:
            product = self.get_product_by_id(product_id)
            if product:
                products[product_id] = product
                
        return products 