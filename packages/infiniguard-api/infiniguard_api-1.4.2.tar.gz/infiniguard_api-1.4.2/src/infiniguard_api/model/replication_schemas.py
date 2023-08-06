from marshmallow import Schema
from marshmallow.fields import String, Nested, Boolean, Int
from marshmallow import validate, ValidationError
from marshmallow.decorators import validates_schema
from infiniguard_api.model.base_schema import PaginatedResponseSchema


class ReplicationSourceCreateSchema(Schema):
    hostid = String(required=True, description='Source host', example='host1')


class ReplicationSourceSchema(Schema):
    ip = String(required=True, description='Source host', example='1.2.3.4')


class ReplicationSourcesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(ReplicationSourceSchema,
                    many=True)


class ReplicationSourcePaginatedSchema(PaginatedResponseSchema):
    result = Nested(ReplicationSourceSchema,
                    many=False)


class ReplicationTargetCreateSchema(Schema):
    hostid = String(required=True,
                    description='Target host',
                    example='host1')
    sourceip = String(required=True,
                      description='Source IP',
                      example='10.10.1.121')
    encrypt = Boolean(default=False,
                      description='Whether to use encryption',
                      example=True)
    encrypttype = String(validate=validate.OneOf(['128', '256']),
                         description='Encryption type',
                         example='128')

    @validates_schema(pass_original=True)
    def validate_encrypt(self, data, original_data, **kwargs):
        if original_data.get('encrypt', None):
            if not original_data.get('encrypttype', None):
                raise ValidationError(" must set 'encrypttype'", "encrypt")


class ReplicationTargetSchema(Schema):
    targethost = String(required=True,
                        description='Target host',
                        example='host1')
    source_ip = String(required=True,
                       description='Source IP',
                       example='10.10.1.121')
    encryption = Boolean(
                        description='Whether to use encryption',
                        example=True)
    encryption_type = String(validate=validate.OneOf(['128-BIT', '256-BIT']),
                             description='Encryption type',
                             example='128')
    program_rep_paused = Boolean(
                                description='Replication is paused by system',
                                example=True)
    user_rep_paused = Boolean(
                             description='Replication is paused by user',
                             example=False)
    nas_rep_paused = Boolean(
                            description='NAS replication is paused',
                            example=False)
    vtl_rep_paused = Boolean(
                            description='VTL replication is paused',
                            example=False)
    rep_revision = String(description='Replication revision')


class ReplicationTargetsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(ReplicationTargetSchema,
                    many=True)


class ReplicationTargetPaginatedSchema(PaginatedResponseSchema):
    result = Nested(ReplicationTargetSchema,
                    many=False)


class OstMappingCreateSchema(Schema):
    replicationip = String(required=True, description='Replication IP', example='10.1.2.3')
    dataip = String(required=True, description='Data IP', example='10.2.3.4')


class OstMappingSchema(Schema):
    replicationip = String(required=True, description='Replication IP',
                           attribute='replication_ip_address',
                           example='10.3.4.5')
    dataip = String(required=True, description='Data IP',
                    attribute='data_ip_address',
                    example='10.4.5.6')


class OstMappingsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstMappingSchema,
                    many=True)


class OstMappingPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstMappingSchema,
                    many=False)

schema_classes = [
    ReplicationSourceCreateSchema,
    ReplicationSourceSchema,
    ReplicationSourcesPaginatedSchema,
    ReplicationSourcePaginatedSchema,
    ReplicationTargetCreateSchema,
    ReplicationTargetSchema,
    ReplicationTargetsPaginatedSchema,
    ReplicationTargetPaginatedSchema,
    OstMappingCreateSchema,
    OstMappingSchema,
    OstMappingsPaginatedSchema,
    OstMappingPaginatedSchema
    ]
