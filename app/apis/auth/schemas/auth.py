from marshmallow import Schema, fields

class LoginSchema(Schema):
    email = fields.String(required=True, metadata={"description": "User email"})
    password = fields.String(required=True, metadata={"description": "User password"})

class LoginResponse(Schema):
    access_token = fields.Str(metadata={"description": "JWT access token"})
    refresh_token = fields.Str(metadata={"description": "JWT refresh token"})
    user_id = fields.Str(metadata={"description": "User ID"})
    email = fields.Str(metadata={"description": "User email"})

class AccessCodeGenerationSchema(Schema):
    """Schema for generating an access code"""
    id = fields.UUID(dump_only=True, metadata={"description": "Access code ID"})
    code = fields.String(dump_only=True, metadata={"description": "Access code"})
    referral_email = fields.String(metadata={"description": "Email of the referral"})
    referral_phone = fields.String(allow_none=True, metadata={"description": "Phone of the referral"})
    health_care_center_email = fields.String(allow_none=True, metadata={"description": "Email of the health care center to find by email"})
    health_care_center_phone = fields.String(allow_none=True, metadata={"description": "Phone of the health care center to find by phone"})
    health_care_center_id = fields.UUID(dump_only=True, allow_none=True, metadata={"description": "ID of the health care center"})
    health_care_center_name = fields.String(dump_only=True, allow_none=True, metadata={"description": "Name of the health care center"})
    expiry_days = fields.Integer(dump_default=7, metadata={"description": "Number of days until the code expires"})
    created_at = fields.String(dump_only=True, metadata={"description": "Creation date"})
    expires_at = fields.String(dump_only=True, metadata={"description": "Expiration date"})
    is_active = fields.Boolean(dump_only=True, metadata={"description": "Is active"})

class AccessCodeFilterSchema(Schema):
    """Schema for filtering access codes"""
    search = fields.String(metadata={"description": "Search term across code, email, and phone"})
    email = fields.String(metadata={"description": "Filter by email (partial match)"})
    is_used = fields.Boolean(metadata={"description": "Filter by used status"})
    is_active = fields.Boolean(metadata={"description": "Filter by active status"})
    role = fields.String(metadata={"description": "Filter by role"})
    page = fields.Integer(load_default=1, metadata={"description": "Page number for pagination"})
    page_size = fields.Integer(load_default=20, metadata={"description": "Number of items per page"})
    sort_by = fields.String(load_default="created_at", metadata={"description": "Field to sort by"})
    sort_order = fields.String(load_default="desc", metadata={"description": "Sort order (asc or desc)"}) 