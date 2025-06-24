from marshmallow import Schema, fields
from app.shared.domain.schema.common_errors import ErrorResponseSchema
from .user import UserSchema
from .auth import AccessCodeGenerationSchema, LoginResponse

class AdminRegistrationResponseSchema(Schema):
    code = fields.Int(metadata={"description": "Admin registration code"})
    message = fields.Str(metadata={"description": "Admin registration message"})
    data = fields.Nested(UserSchema, metadata={"description": "Admin registration data"})
    
    

class LogInResponseSchema(Schema):
    code = fields.Int(metadata={"description": "Login code"})
    message = fields.Str(metadata={"description": "Login message"})
    data = fields.Nested(LoginResponse, metadata={"description": "Login data"})


class UserResponseSchema(Schema):
    data = fields.Nested(UserSchema, metadata={"description": "User data"})
    message = fields.Str(metadata={"description": "User message"})
    success = fields.Bool(metadata={"description": "User success"})

class AccessCodeResponseSchema(Schema):
    data = fields.Nested(AccessCodeGenerationSchema, metadata={"description": "Access code data"})
    message = fields.Str(metadata={"description": "Response message"})
    success = fields.Bool(metadata={"description": "Success status"})

class AdminRegistrationErrorResponseSchema(ErrorResponseSchema):
    errors = fields.Dict(required=False, metadata={"description": "The errors of the response"}) 

class AccessCodeEntitySchema(Schema):
    code = fields.Str(metadata={"description": "Access code"})
    created_at = fields.Str(metadata={"description": "Created at"})
    expires_at = fields.Str(metadata={"description": "Expires at"})
    health_care_center_id = fields.Str(metadata={"description": "Health care center id"})
    id = fields.Str(metadata={"description": "Id"})
    is_active = fields.Bool(metadata={"description": "Is active"})
    is_used = fields.Bool(metadata={"description": "Is used"})
    updated_at = fields.Str(metadata={"description": "Updated at"})
    
class AccessCodeItemSchema(Schema):
    access_code_entity = fields.Nested(AccessCodeEntitySchema, metadata={"description": "Access code entity"})
    health_care_center_name = fields.Str(metadata={"description": "Health care center name"})
    is_valid = fields.Bool(metadata={"description": "Is valid"})
    message = fields.Str(metadata={"description": "Message"})


    
class AccessCodeValidationResponseSchema(Schema):
    data = fields.Nested(AccessCodeItemSchema, metadata={"description": "Access code data"})
    message = fields.Str(metadata={"description": "Response message"})
    success = fields.Bool(metadata={"description": "Success status"})

class AccessCodeListResponseSchema(Schema):
    data = fields.List(fields.Nested(AccessCodeItemSchema), metadata={"description": "Access code list"})
    message = fields.Str(metadata={"description": "Response message"})
    success = fields.Bool(metadata={"description": "Success status"})

