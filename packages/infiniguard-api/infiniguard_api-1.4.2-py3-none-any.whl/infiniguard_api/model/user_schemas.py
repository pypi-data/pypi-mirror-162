from marshmallow import Schema, validate
from marshmallow.fields import String, Int, List, Nested
from infiniguard_api.model.base_schema import PaginatedResponseSchema, NonPaginatedResponseSchema
from infiniguard_api.model.models import USER_ROLES


class UserSchema(Schema):
    name = String(required=True, description='User name', example='username')
    password = String(description='User Password', required=True)
    description = String(description='User Description',
                         example='User Description')
    role = String(validate=validate.OneOf(USER_ROLES),
                  default=USER_ROLES[0],
                  required=True,
                  description='User role: backup or AIR or workgoup',
                  example=USER_ROLES[0])

class UserEditSchema(UserSchema):
    password = String(description='User Password')
    

class UsersPaginatedSchema(PaginatedResponseSchema):
    result = Nested(UserSchema,
                    exclude=('password',),
                    many=True,
                    example=[
                        {
                            "description": "User description",
                            "name": "username",
                            "role": "backupuser"
                        }])


class UserNonPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(UserSchema,
                    exclude=('password',),
                    many=False,
                    example=[
                        {
                            "description": "User description",
                            "name": "username",
                            "role": "backupuser"
                        }])


schema_classes = [ UserSchema, UserEditSchema, UsersPaginatedSchema, UserNonPaginatedSchema ]
