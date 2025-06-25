from marshmallow import Schema, fields, validate
from datetime import datetime
from app.services.product_service.domain.enums.product_status import ProductStatus



class ProductFieldsSchema(Schema):
    id= fields.UUID(dump_only=True)
    name=fields.Str()
    description=fields.Str()    
    brand= fields.Str()
    category_id= fields.UUID()
    dosage_form= fields.Str()
    strength=fields.Str()
    package=fields.Str()
    image_url=fields.Str()
    status=fields.Enum(ProductStatus)
    created_at=fields.DateTime(dump_only=True)
    updated_at=fields.DateTime(dump_only=True)

class InventoryFieldsSchema(Schema):
    quantity=fields.Int()
    price=fields.Float()
    max_stock=fields.Int()
    min_stock=fields.Int()
    expiry_date=fields.Date()
    id= fields.UUID(dump_only=True)
    product_id= fields.UUID(dump_only=True)
    supplier_id=fields.UUID()

class ProductSchema(Schema):
    """Schema for product creation and update"""
    id = fields.UUID(dump_only=True, metadata={"description": "The product ID"})
    product_fields=fields.Nested(ProductFieldsSchema)
    inventory_fields=fields.Nested(InventoryFieldsSchema)

class ProductItemSchema(Schema):
    """Schema for flattened product item in list responses"""
    id = fields.Str(metadata={"description": "The product ID"})
    name = fields.Str(metadata={"description": "Product name"})
    description = fields.Str(metadata={"description": "Product description"})
    price = fields.Float(metadata={"description": "Product price"})
    oldPrice = fields.Float(allow_none=True, metadata={"description": "Previous price"})
    discountPercent = fields.Int(allow_none=True, metadata={"description": "Discount percentage"})
    imageUrl = fields.Str(metadata={"description": "Product image URL"})
    inStock = fields.Bool(metadata={"description": "Whether product is in stock"})
    stockQuantity = fields.Int(metadata={"description": "Available stock quantity"})
    category = fields.Str(metadata={"description": "Product category"})
    manufacturer = fields.Str(metadata={"description": "Product manufacturer"})
    metadata = fields.Dict(allow_none=True, metadata={"description": "Additional product metadata"})
    
class ProductFilterSchema(Schema):
    """Schema for product filtering"""
    name = fields.Str(metadata={"description": "Filter by product name (partial match)"})
    category_id = fields.UUID(metadata={"description": "Filter by category ID"})
    brand = fields.Str(metadata={"description": "Filter by brand (partial match)"})
    is_prescription_required = fields.Bool(metadata={"description": "Filter by prescription requirement"})
    is_active = fields.Bool(metadata={"description": "Filter by active status"})
    min_stock = fields.Int(metadata={"description": "Filter by minimum stock level"})
    has_stock = fields.Bool(metadata={"description": "Filter by stock availability"})
    sort_by = fields.Str(
        validate=validate.OneOf(["name", "created_at", "brand"]),
        dump_default="name",
        metadata={"description": "Field to sort by"}
    )
    sort_direction = fields.Str(
        validate=validate.OneOf(["asc", "desc"]),
        dump_default="asc",
        metadata={"description": "Sort direction"}
    )
    page = fields.Int(dump_default=1, metadata={"description": "Page number"})
    items_per_page = fields.Int(dump_default=20, metadata={"description": "Items per page"})
    # Additional fields for advanced filtering
    min_price = fields.Float(metadata={"description": "Minimum price filter"})
    max_price = fields.Float(metadata={"description": "Maximum price filter"})
    status = fields.Enum(ProductStatus, metadata={"description": "Filter by product status"})
    days_threshold = fields.Int(metadata={"description": "Days threshold for expiry filtering"})
    threshold_percentage = fields.Float(metadata={"description": "Threshold percentage for low stock"})

class ProductSearchSchema(Schema):
    """Schema for product search with advanced options"""
    search = fields.Str(metadata={"description": "Search term for name, description, brand"})
    category_id = fields.UUID(metadata={"description": "Filter by category ID"})
    brand = fields.Str(metadata={"description": "Filter by brand"})
    min_price = fields.Float(metadata={"description": "Minimum price"})
    max_price = fields.Float(metadata={"description": "Maximum price"})
    status = fields.Enum(ProductStatus, metadata={"description": "Product status filter"})
    in_stock_only = fields.Bool(dump_default=False, metadata={"description": "Show only products in stock"})
    page = fields.Int(dump_default=1, metadata={"description": "Page number"})
    page_size = fields.Int(dump_default=20, metadata={"description": "Items per page"})
    sort_by = fields.Str(
        validate=validate.OneOf(["name", "price", "created_at", "brand"]),
        dump_default="name",
        metadata={"description": "Field to sort by"}
    )
    sort_direction = fields.Str(
        validate=validate.OneOf(["asc", "desc"]),
        dump_default="asc",
        metadata={"description": "Sort direction"}
    )

class BulkProductSchema(Schema):
    """Schema for bulk product operations"""
    products = fields.List(
        fields.Nested(ProductSchema),
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "List of products to create"}
    )

class ProductResponseSchema(Schema):
    """Schema for product response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(ProductSchema)
    
    
class ProductPaginatedSchema(Schema):
    """Schema for paginated product response"""
    items = fields.List(fields.Nested(ProductItemSchema), metadata={"description": "List of products"})
    total = fields.Int(metadata={"description": "Total number of products"})
    page = fields.Int(metadata={"description": "Current page number"})
    page_size = fields.Int(metadata={"description": "Items per page"})
    total_pages = fields.Int(metadata={"description": "Total number of pages"})

class ProductPaginatedResponseSchema(Schema):
    """Schema for product response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(ProductPaginatedSchema)

class ProductExpiryReportSchema(Schema):
    """Schema for product expiry report"""
    product = fields.Nested(ProductResponseSchema, metadata={"description": "Product information"})
    expiry_date = fields.DateTime(metadata={"description": "Expiry date"})
    quantity = fields.Int(metadata={"description": "Quantity expiring"})
    total_expiring = fields.Int(metadata={"description": "Total quantity expiring"})

class ProductInventoryValueReportSchema(Schema):
    """Schema for product inventory value report"""
    product = fields.Nested(ProductResponseSchema, metadata={"description": "Product information"})
    quantity = fields.Int(metadata={"description": "Current quantity"})
    price = fields.Float(metadata={"description": "Unit price"})
    total_value = fields.Float(metadata={"description": "Total inventory value"})

class StockStatusSchema(Schema):
    """Schema for product stock status"""
    product_id = fields.UUID(metadata={"description": "Product ID"})
    is_available = fields.Bool(metadata={"description": "Whether product is available"})
    remaining_stock = fields.Int(metadata={"description": "Remaining stock quantity"})
    warnings = fields.List(fields.Str(), metadata={"description": "Stock warnings"})
    status = fields.List(fields.Str(), metadata={"description": "Stock status codes"})
    days_until_expiry = fields.Int(allow_none=True, metadata={"description": "Days until expiry"})
    
class ErrorResponseSchema(Schema):
    """Schema for error responses"""
    success = fields.Bool(metadata={"description": "Indicates if the request was successful"})
    message = fields.Str(metadata={"description": "A message describing the error"})
    errors = fields.Dict(metadata={"description": "Detailed error messages"})
    
class SuccessResponseSchema(Schema):
    """Schema for success responses"""
    success = fields.Bool(metadata={"description": "Indicates if the request was successful"})
    message = fields.Str(metadata={"description": "A message describing the success"})
    data = fields.Dict(metadata={"description": "Response data"})
