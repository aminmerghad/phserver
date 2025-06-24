from marshmallow import Schema, fields, validate
from datetime import datetime

class CategoryFieldsSchema(Schema):
    """Schema for category fields"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    parent_id = fields.UUID(allow_none=True)
    image_url = fields.Str(allow_none=True)
    is_active = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CategorySchema(Schema):
    """Schema for category creation and update"""
    id = fields.UUID(dump_only=True, metadata={"description": "The category ID"})
    category_fields = fields.Nested(CategoryFieldsSchema)

class CategoryFilterSchema(Schema):
    """Schema for category filtering"""
    name = fields.Str(metadata={"description": "Filter by category name (partial match)"})
    parent_id = fields.UUID(metadata={"description": "Filter by parent category ID"})
    is_active = fields.Bool(metadata={"description": "Filter by active status"})
    sort_by = fields.Str(
        validate=validate.OneOf(["name", "created_at"]),
        dump_default="name",
        metadata={"description": "Field to sort by"}
    )
    sort_direction = fields.Str(
        validate=validate.OneOf(["asc", "desc"]),
        dump_default="asc",
        metadata={"description": "Sort direction"}
    )
    page = fields.Int(dump_default=1, validate=validate.Range(min=1), metadata={"description": "Page number"})
    items_per_page = fields.Int(dump_default=20, validate=validate.Range(min=1), metadata={"description": "Items per page"})

class CategoryResponseSchema(Schema):
    """Schema for category response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(CategorySchema)

class CategoryPaginatedSchema(Schema):
    """Schema for paginated category response"""
    items = fields.List(fields.Nested(CategorySchema), metadata={"description": "List of categories"})
    total_items = fields.Int(metadata={"description": "Total number of categories"})
    page = fields.Int(metadata={"description": "Current page number"})
    page_size = fields.Int(metadata={"description": "Items per page"})
    total_pages = fields.Int(metadata={"description": "Total number of pages"})

class CategoryPaginatedResponseSchema(Schema):
    """Schema for category response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(CategoryPaginatedSchema)

class DeleteCategoryResponseSchema(Schema):
    """Schema for the response of a delete operation"""
    id = fields.UUID(dump_only=True)
    success = fields.Boolean(dump_only=True)

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