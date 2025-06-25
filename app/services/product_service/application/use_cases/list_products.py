from math import ceil
from typing import List, Dict, Any, Optional
import logging

from pydantic import BaseModel

from app.services.product_service.application.queries.get_products_by_filter import GetProductsByFilterQuery
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto

class ProductItemDTO(BaseModel):
    id: str
    name: str
    description: str
    price: Optional[float] = 0.0
    oldPrice: Optional[float] = None
    discountPercent: Optional[int] = None
    imageUrl: str
    inStock: Optional[bool] = True
    stockQuantity: Optional[int] = 0
    category: str
    manufacturer: str
    metadata: Optional[Dict[str, Any]] = None

class ProductListDTO(BaseModel):
    items: List[ProductItemDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

# Configure logger
logger = logging.getLogger(__name__)

class ListProductsUseCase:
    """
    Use case for listing products with filtering and pagination.
    """
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, query: GetProductsByFilterQuery) -> Dict[str, Any]:
        logger.info(f"Listing products with filters: {query.filters}")
        
        # Get products from repository with pagination
        products, total_count = self._get_products(query)
        
        # Calculate pagination info
        total_pages = ceil(total_count / query.page_size) if total_count > 0 else 1
        
        # Create response DTO
        response = self._create_product_list_dto(products, total_count, query.page, query.page_size, total_pages)
        
        logger.info(f"Retrieved {total_count} products (page {query.page} of {total_pages})")
        return response.model_dump()
    
    def _get_products(self, query: GetProductsByFilterQuery):
        products = self._uow.product_repository.list(
            filters=query.filters,
            page=query.page,
            page_size=query.page_size
        )
        
        # Get total count for pagination
        total_count = self._uow.product_repository.count(filters=query.filters)
        
        return products, total_count
    
    def _create_product_list_dto(self, products, total_count, page, page_size, total_pages) -> ProductListDTO:
        product_dtos = []
        
        for product in products:
            # Get inventory data for this product if available
            inventory_data = self._get_inventory_data(product.id)
            
            # Get category name through relationship
            category_name = ""
            if hasattr(product, 'category') and product.category:
                category_name = product.category.name
            
            # Create flattened DTO structure
            product_dto = ProductItemDTO(
                id=str(product.id),
                name=product.name or "",
                description=product.description or "",
                price=inventory_data.get('price', 0.0) if inventory_data else 0.0,
                oldPrice=None,  # You can add this logic if you have old price data
                discountPercent=None,  # You can add this logic if you have discount data
                imageUrl=product.image_url or "",
                inStock=inventory_data.get('quantity', 0) > 0 if inventory_data else False,
                stockQuantity=inventory_data.get('quantity', 0) if inventory_data else 0,
                category=category_name,  # Using actual category name
                manufacturer=product.brand or "",  # Using brand as manufacturer
                metadata={
                    "dosage_form": product.dosage_form,
                    "strength": product.strength,
                    "package": product.package,
                    "brand": product.brand,  # Keep brand in metadata for reference
                    "status": str(product.status) if hasattr(product, 'status') else None,
                    "category_id": str(product.category_id) if product.category_id else None,
                    "created_at": str(product.created_at) if hasattr(product, 'created_at') else None,
                    "updated_at": str(product.updated_at) if hasattr(product, 'updated_at') else None,
                    "max_stock": inventory_data.get('max_stock') if inventory_data else None,
                    "min_stock": inventory_data.get('min_stock') if inventory_data else None,
                    "expiry_date": str(inventory_data.get('expiry_date')) if inventory_data and inventory_data.get('expiry_date') else None,
                    "supplier_id": str(inventory_data.get('supplier_id')) if inventory_data and inventory_data.get('supplier_id') else None
                }
            )
            
            product_dtos.append(product_dto)
        
        return ProductListDTO(
            items=product_dtos,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def _get_inventory_data(self, product_id) -> Optional[Dict[str, Any]]:
        # This would typically query the inventory service or a local cache
        # For now, we'll just return a simplified approach
        try:
            inventory = self._uow.inventory_repository.get_by_product_id(product_id) if hasattr(self._uow, 'inventory_repository') else None
            
            if inventory:
                return inventory.model_dump()
            return None
        except Exception as e:
            logger.warning(f"Error retrieving inventory data for product {product_id}: {str(e)}")
            return None