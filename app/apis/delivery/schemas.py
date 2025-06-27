from marshmallow import Schema, fields, validate
from app.shared.domain.schema.common_errors import ErrorResponseSchema


class DeliveryLocationSchema(Schema):
    health_care_center_id = fields.UUID(required=True, description="Health care center ID")
    health_care_center_name = fields.String(required=True, description="Health care center name")
    address = fields.String(required=True, description="Full address")
    latitude = fields.Float(required=True, description="GPS latitude coordinate")
    longitude = fields.Float(required=True, description="GPS longitude coordinate")
    phone = fields.String(allow_none=True, description="Contact phone number")
    email = fields.String(allow_none=True, description="Contact email address")


class DeliveryOrderSchema(Schema):
    order_id = fields.UUID(required=True, description="Order ID")
    user_id = fields.UUID(required=True, description="User ID")
    total_amount = fields.Float(required=True, description="Total order amount")
    items_count = fields.Integer(required=True, description="Number of items in order")
    notes = fields.String(allow_none=True, description="Order notes")
    created_at = fields.DateTime(allow_none=True, description="Order creation timestamp")


class DeliveryRouteSchema(Schema):
    id = fields.UUID(allow_none=True, description="Route ID")
    route_name = fields.String(required=True, description="Route name")
    status = fields.String(required=True, description="Delivery status")
    estimated_delivery_time = fields.DateTime(allow_none=True, description="Estimated delivery time")
    total_amount = fields.Float(required=True, description="Total amount for all orders in route")
    total_items_count = fields.Integer(required=True, description="Total items count for all orders")
    created_at = fields.DateTime(allow_none=True, description="Route creation timestamp")
    updated_at = fields.DateTime(allow_none=True, description="Route last update timestamp")
    location = fields.Nested(DeliveryLocationSchema, required=True, description="Delivery location")
    orders = fields.List(fields.Nested(DeliveryOrderSchema), required=True, description="Orders in this route")


class DeliverySummarySchema(Schema):
    total_routes = fields.Integer(required=True, description="Total number of delivery routes")
    processing_orders_count = fields.Integer(required=True, description="Number of processing orders")
    total_estimated_deliveries = fields.Integer(required=True, description="Total estimated deliveries")


class DeliveryRoutesResponseSchema(Schema):
    routes = fields.List(fields.Nested(DeliveryRouteSchema), required=True, description="List of delivery routes")
    summary = fields.Nested(DeliverySummarySchema, required=True, description="Summary information")


class DeliveryQuerySchema(Schema):
    include_location_details = fields.Boolean(
        default=True,
        description="Whether to include detailed location information"
    )
    group_by_location = fields.Boolean(
        default=True,
        description="Whether to group orders by health care center location"
    )
    limit = fields.Integer(
        validate=validate.Range(min=1, max=100),
        allow_none=True,
        description="Maximum number of routes to return"
    )


class DeliveryRoutesApiResponseSchema(Schema):
    code = fields.Integer(description="Response code")
    message = fields.String(description="Response message")
    data = fields.Nested(DeliveryRoutesResponseSchema, description="Delivery routes data") 