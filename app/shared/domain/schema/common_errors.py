from marshmallow import Schema, fields

class ErrorResponseSchema(Schema):
    code = fields.Int(metadata={"description": "The HTTP status code of the error"})
    status = fields.Str(dump_default="error", metadata={"description": "The status of the response"})
    message = fields.Str(metadata={"description": "A message describing the error"})
    errors=fields.Str(metadata={"description": "A dict describing the error"})
