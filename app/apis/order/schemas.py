from marshmallow import Schema, fields, validate
from decimal import Decimal

from app.services.order_service.domain.value_objects.order_status import OrderStatus

class OrderItemSchema(Schema):
    id = fields.Str(dump_only=True)
    product_id = fields.UUID(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))  # Changed to Decimal and made required
    total_price = fields.Decimal(dump_only=True)  # Changed to Decimal
    name = fields.Str(required=False)
    
class OrderSchema(Schema):
    order_id = fields.UUID(dump_only=True)
    consumer_id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema))
    status = fields.Enum(enum=OrderStatus, by_value=True)
    total_amount = fields.Decimal()
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)

class OrderFilterSchema(Schema):
    user_id = fields.UUID(required=False, description="Filter by user ID")
    status = fields.String(required=False, description="Filter by order status")
    start_date = fields.DateTime(required=False, description="Filter by start date")
    end_date = fields.DateTime(required=False, description="Filter by end date")
    min_amount = fields.Decimal(required=False, description="Filter by minimum amount")
    max_amount = fields.Decimal(required=False, description="Filter by maximum amount")
    page = fields.Integer(required=False, missing=1, description="Page number")
    per_page = fields.Integer(required=False, missing=10, description="Items per page")

class CreateOrderSchema(Schema):
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    notes = fields.Str(required=False, allow_none=True)

class UpdateOrderStatusSchema(Schema):
    status = fields.Enum(enum=OrderStatus, by_value=True, required=True)
    notes = fields.Str(required=False, allow_none=True)

# Bulk Update Schemas
class BulkUpdateOrderItemSchema(Schema):
    """Schema for a single order update in bulk operation"""
    order_id = fields.UUID(required=True, description="Order ID to update")
    status = fields.Enum(enum=OrderStatus, by_value=True, required=False, description="New status for the order")
    notes = fields.Str(required=False, allow_none=True, description="New notes for the order")

class BulkUpdateOrderSchema(Schema):
    """Schema for bulk order update request"""
    updates = fields.List(
        fields.Nested(BulkUpdateOrderItemSchema), 
        required=True, 
        validate=validate.Length(min=1, max=100),
        description="List of order updates (max 100)"
    )
    
# Bulk Update Response Schemas
class BulkUpdateOrderItemResultSchema(Schema):
    """Schema for individual order update result"""
    order_id = fields.UUID(required=True, description="Order ID")
    success = fields.Bool(required=True, description="Whether the update was successful")
    old_status = fields.Enum(enum=OrderStatus, by_value=True, allow_none=True, description="Previous order status")
    new_status = fields.Enum(enum=OrderStatus, by_value=True, allow_none=True, description="New order status")
    error_message = fields.Str(allow_none=True, description="Error message if update failed")
    error_code = fields.Str(allow_none=True, description="Error code if update failed")

class BulkUpdateOrderResultSchema(Schema):
    """Schema for bulk update response data"""
    total_attempted = fields.Int(required=True, description="Total number of orders attempted to update")
    total_successful = fields.Int(required=True, description="Number of successfully updated orders")
    total_failed = fields.Int(required=True, description="Number of failed order updates")
    success_rate = fields.Float(dump_only=True, description="Success rate percentage")
    results = fields.List(
        fields.Nested(BulkUpdateOrderItemResultSchema), 
        required=True, 
        description="Detailed results for each order"
    )

class PaginationSchema(Schema):
    page = fields.Int(description="Current page number")
    per_page = fields.Int(description="Items per page")
    pages = fields.Int(description="Total pages")
    total = fields.Int(description="Total items")

class OrderListSchema(Schema):
    orders = fields.Nested(OrderSchema,many=True)
    pagination=fields.Nested(PaginationSchema)

class OrderListResponseSchema(Schema):
    code = fields.Int(description="order code")
    message = fields.Str(description="order message")
    data = fields.Nested(OrderListSchema, description="order data")
    
class OrderResponseSchema(Schema):
    code = fields.Int(description="order code")
    message = fields.Str(description="order message")
    data = fields.Nested(OrderSchema, description="order data")

class BulkUpdateOrderResponseSchema(Schema):
    """Schema for bulk update API response"""
    code = fields.Int(description="Response code")
    message = fields.Str(description="Response message")
    data = fields.Nested(BulkUpdateOrderResultSchema, description="Bulk update results")


