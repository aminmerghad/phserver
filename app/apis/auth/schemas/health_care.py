from marshmallow import Schema, fields
from app.shared.domain.schema.common_errors import ErrorResponseSchema

class HealthCareCenterSchema(Schema):
    """Schema for creating or updating a health care center"""
    name = fields.String(required=True, metadata={"description": "Name of the health care center"})
    address = fields.String(required=True, metadata={"description": "Address of the health care center"})
    phone = fields.String(required=True, metadata={"description": "Contact phone number"})
    email = fields.String(required=True, metadata={"description": "Contact email address"})
    is_active = fields.Boolean(dump_default=True, metadata={"description": "Whether the center is active"})
    latitude = fields.Float(required=False, metadata={"description": "Latitude of the health care center"})
    longitude = fields.Float(required=False, metadata={"description": "Longitude of the health care center"})


class HealthCareCenterResponseSchema(Schema):
    """Schema for health care center response"""
    id = fields.UUID(required=True, metadata={"description": "Health care center ID"})
    name = fields.String(required=True, metadata={"description": "Name of the health care center"})
    address = fields.String(required=True, metadata={"description": "Address of the health care center"})
    phone = fields.String(required=True, metadata={"description": "Contact phone number"})
    email = fields.String(required=True, metadata={"description": "Contact email address"})
    is_active = fields.Boolean(required=True, metadata={"description": "Whether the center is active"})
    created_at = fields.DateTime(dump_only=True, metadata={"description": "Creation timestamp"})
    updated_at = fields.DateTime(dump_only=True, metadata={"description": "Last update timestamp"})

class HealthCareCenterFilterSchema(Schema):
    """Schema for filtering health care centers"""
    search = fields.String(metadata={"description": "Search term across name and email"})
    name = fields.String(metadata={"description": "Filter by health care center name (partial match)"})
    email = fields.String(metadata={"description": "Filter by email address (partial match)"})
    is_active = fields.Boolean(metadata={"description": "Filter by active status"})
    page = fields.Integer(load_default=1, metadata={"description": "Page number for pagination"})
    page_size = fields.Integer(load_default=20, metadata={"description": "Number of items per page"})
    sort_by = fields.String(load_default="name", metadata={"description": "Field to sort by"})
    sort_order = fields.String(load_default="asc", metadata={"description": "Sort order (asc or desc)"})

class HealthCareCenterListItemSchema(Schema):
    """Schema for a health care center list item"""
    id = fields.UUID(required=True, metadata={"description": "Health care center ID"})
    name = fields.String(required=True, metadata={"description": "Name of the health care center"})
    address = fields.String(required=True, metadata={"description": "Address of the health care center"})
    phone = fields.String(required=True, metadata={"description": "Contact phone number"})
    email = fields.String(required=True, metadata={"description": "Contact email address"})
    is_active = fields.Boolean(required=True, metadata={"description": "Whether the center is active"})

class HealthCareCenterListResponseSchema(Schema):
    """Schema for paginated list of health care centers"""
    items = fields.List(fields.Nested(HealthCareCenterListItemSchema), required=True, metadata={"description": "List of health care centers"})
    total = fields.Integer(required=True, metadata={"description": "Total number of health care centers matching the filter"})
    page = fields.Integer(required=True, metadata={"description": "Current page number"})
    page_size = fields.Integer(required=True, metadata={"description": "Number of items per page"})
    pages = fields.Integer(required=True, metadata={"description": "Total number of pages"}) 