import os
from marshmallow import Schema
from marshmallow.fields import String, Int, List, Nested, Boolean, Float
from marshmallow import validate, ValidationError, pre_dump
from marshmallow.decorators import validates_schema
from infiniguard_api.model.user_schemas import UserSchema
from infiniguard_api.model.base_schema import PaginatedResponseSchema


class OstStorageserverCreateSchema(Schema):
    name = String(required=True, description='OST storage server name',
                  example='server1')
    maxconnect = Int(missing=300,
                     validate=validate.Range(min=0, max=65536),
                     description='Maximum number of connections allowed to the storage server',
                     example=200)
    target = String(description='Replication target name/IP',
                    example='10.10.1.110')
    desc = String(description='Brief description of the storage server',
                  example='server1 description')
    concurrentopdup = Boolean(
                             description='Whether Concurrent Optimized Duplication is enabled',
                             example=True)


class OstStorageserverSchema(Schema):
    name = String(required=True,
                  description='OST storage server name',
                  attribute='server_name',
                  example='server1')
    lsu_count = Int(description='Amount of LSU in the storage server', example=1)
    maxconnect = Int(default=300, validate=validate.Range(min=0, max=65536),
                     description='Maximum number of connections allowed to the storage server',
                     attribute='max_connections',
                     example=200)
    active_connections = Int(
        description='Current number of connections to the storage server',
        example=5)
    backup_images = Int(
        description='Amount of backup images in the storage server',
        example=40)
    desc = String(description='Brief description of the storage server',
                  attribute='description',
                  example='server1 description')
    concurrentopdup = Boolean(
        description='Whether Concurrent Optimized Duplication is enabled',
        attribute='concurrent_op_dup',
        example=True)
    allowed_replication_targets = List(
        String, description='List of allowed replication targets')
    
    @pre_dump
    def _targets_to_list(self, out_data, **kwargs):
        allowed_replication_targets = out_data.get('allowed_replication_targets')
        out_data['allowed_replication_targets'] = allowed_replication_targets.split(',') if allowed_replication_targets else []
        return out_data


class OstStorageserversPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstStorageserverSchema,
                    many=True)


class OstStorageserverPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstStorageserverSchema,
                    many=False)


class OstLsuCreateSchema(Schema):
    name = String(description='LSU name',
                  example='lsu1')
    capacity = Int(description='Maximum capacity of LSU',
                   example=200)
    storage_server = String(required=True,
                            description='Parent storage server name',
                            attribute='storageserver',
                            example='server1')
    desc = String(description='LSU description',
                  example='lsu1 on server1')

    @validates_schema(pass_original=True)
    def validate_capacity(self, data, original_data, **kwargs):
        capacity = int(original_data.get('capacity', 0))
        if capacity != 0:
            if not original_data.get('name', None):
                raise ValidationError("missing 'name'", "capacity")
        else:
            if original_data.get('name', None):
                raise ValidationError(
                    "'name' will be set to '_PhysicalLSU' when capacity is not set")

class OstLsuEditSchema(Schema):
    name = String(required=True,
                  description='LSU name',
                  example='lsu1')
    desc = String(description='LSU description',
                  example='lsu1 on server1')
    capacity = Int(description='Maximum capacity of LSU',
                   example=200)

    @validates_schema(pass_original=True)
    def validate_capacity(self, data, original_data, **kwargs):
        if original_data.get('name', None) == '_PhysicalLSU':
            if original_data.get('capacity', None):
                raise ValidationError(
                    "can not modify capacity for _PhysicalLSU", "capacity")


class OstLsuSchema(Schema):
    lsu_name = String(required=True,
                      description='LSU name',
                      example='lsu1')
    server_name = String(
        required=True,
        description='Parent storage server name',
        example='server1')
    physical_capacity = String(required=True,
                               description='Physical capacity',
                               example=200)
    backup_images = Int(description='Amount of backup images in the LSU',
                        example=200)
    desc = String(description='LSU description',
                  attribute='description',
                  example='lsu1 on server1')
    ost_air = Boolean(
                     description='Whether AIR replication is enabled',
                     example=False)
    air_user = String(description='AIR user name',
                      example='user1')
    target_host_id = String(description='Target host IP/name',
                            example='10.10.1.100')
    target_server_name = String(description='Target host storage server name',
                                example='targetserver')
    target_lsu_name = String(description='Target host LSU name',
                             example='targetlsu')


class OstLsusPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstLsuSchema,
                    many=True)


class OstLsuPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstLsuSchema,
                    many=False)


class OstAirCreateSchema(Schema):
    source_storage_server = String(required=True,
                                   description='Source storage server name',
                                   attribute='sourcess',
                                   example='server1')
    airuser = String(description='AIR user name',
                     example='user1')
    source_lsu = String(description='Source LSU name',
                        attribute='sourcelsu',
                        example='lsu1')
    target_storage_server = String(description='Target storage server name',
                                   attribute='targetss',
                                   example='targetserver')
    target = String(description='Target host IP/name',
                    example='10.10.1.101')
    target_lsu = String(description='Target LSU name',
                        attribute='targetlsu',
                        example='targetlsu')
    operation = Boolean(
                       description='Enable or disable storage server AIR replication',
                       example=False)

class OstAirusersPaginatedSchema(PaginatedResponseSchema):
    result = Nested(UserSchema,
                    many=True)


class OstAiruserPaginatedSchema(PaginatedResponseSchema):
    result = Nested(UserSchema,
                    many=False)

class OstTlscertificateCreateSchema(Schema):
    certificate = String(description='OST TLS certificate')
    privatekey = String(description='OST TLS privatekey')
    certificateauthority = String(description='Certificate authority')
    rejectionlist = String(description='Rejection list')

    @validates_schema(pass_original=True)
    def validate_files(self, data, original_data, **kwargs):
        self.validate_file_exist(original_data, 'certificate')
        self.validate_file_exist(original_data, 'privatekey')
        self.validate_file_exist(original_data, 'certificateauthority')
        self.validate_file_exist(original_data, 'rejectionlist')

    def validate_file_exist(self, data, file_name):
        file_name = data.get(file_name, None)
        if file_name:
            if not os.path.exists(file_name):
                raise ValidationError("file not exist", file_name)


class OstTlscertificateSchema(Schema):
    tls_file_name = String(required=True,
                           description='OST TLS certificate file name')
    installed_time = String(required=True,
                            description='OST TLS certificate installation time')
    expiration_time = String(required=True,
                             description='OST TLS certificate expiration time')
    status = String(required=True, description='OST TLS certificate status')


class OstTlscertificatesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstTlscertificateSchema,
                    many=True)


class OstTlscertificatePaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstTlscertificateSchema,
                    many=False)


class OstsettingSchema(Schema):
    netboost = Boolean(
                      description='Whether OST NetBoost is enabled',
                      attribute='accent',
                      example=True)
    netboost_enabled_first_time = Boolean(
        description='Whether this is the first activation of NetBoost',
        attribute='accent_enabled_first_time',
        example=True)
    encryption = Boolean(
                        description='Whether OST NetBoost uses encryption',
                        example=True)
    encryption_type = String(validate=validate.OneOf(
        ['aes128', 'aes256', 'tlsaes256', 'none']),
        description='OST NetBoost encryption type',
        example='aes256')

class OstsettingEditSchema(Schema):
    netboost = Boolean(
                      description='Whether OST NetBoost is enabled',
                      attribute='accent',
                      example=True)
    encryption = Boolean(
                        description='Whether OST NetBoost uses encryption',
                        example=True)
    encryptiontype = String(validate=validate.OneOf(
        ['aes128', 'aes256', 'tlsaes256']),
        description='OST NetBoost encryption type',
        example='aes256')


class OstsettingPaginatedSchema(PaginatedResponseSchema):
    result = Nested(OstsettingSchema,
                    many=False)

class OstBasicStatisticsSchema(Schema):
    client_id = String(required=True, description='Client IP/name')
    media_server_count = Int(required=True, description='Media server count')
    time_stamp = String(required=True, description='Time stamp')
    measure_period = String(required=True, description='Measure period')


class OstAccentStatisticsSchema(Schema):
    before_netboost_received = String(
        attribute='before_accent_received',
        description='Bytes received before NetBoost')
    after_netboost_received = String(
        attribute='after_accent_received',
        description='Bytes received after NetBoost')
    before_netboost_sent = String(
        attribute='before_accent_sent',
        description='Bytes sent before NetBoost')
    after_netboost_sent = String(
        attribute='after_accent_sent',
        description='Bytes sent after NetBoost')
    unique_data = Int(description='Bytes unique data')
    receive_ratio = String(description='Receive ratio')
    ethernet_bandwidth_rate_received = String(
        description='Received etherhet bandwidth')
    ethernet_bandwidth_rate_sent = String(
        description='Sent ethernet bandwidth')
    virtual_rate_recieved = String(description='Apparent received rate')
    virtual_rate_sent = String(description='Apparent sent rate')
    bandwidth_reduction = String(description='Bandwidth reduction')
    ethernet_in = String(description='Ethernet in rate')
    inline = String(description='Inline rate')


class OstOptimizedDupStatisticsSchema(Schema):
    images_in_progress = Int(description='Images in progress')
    remaining_in_rep_queue = String(
        description='Remaining in replication queue')
    processed_last_60_seconds = String(
        description='Processed bytes in the last minute')
    unique_last_60_seconds = String(
        description='Unique bytes in the last minute')
    processed_to_unique_ratio = String(description='Processed to unique ratio')
    ethernet_bandwidth_rate = String(description='Ethernet bandwith rate')
    virtual_rate = String(description='Apparent rate')
    bandwidth_reduction = Float(description='Bandwidth reduction')
    ethernet_in = String(description='Ethernet in rate')
    inline = String(description='Inline rate')


class OstaccentstatsSchema(Schema):
    basic_statistics = Nested(OstBasicStatisticsSchema)
    netboost_statistics = Nested(OstAccentStatisticsSchema)
    optimized_duplication_statistics = Nested(OstOptimizedDupStatisticsSchema)

schema_classes = [
    OstStorageserverCreateSchema,
    OstStorageserverSchema,
    OstStorageserversPaginatedSchema,
    OstStorageserverPaginatedSchema,
    OstLsuCreateSchema,
    OstLsuEditSchema,
    OstLsuSchema,
    OstLsusPaginatedSchema,
    OstLsuPaginatedSchema,
    OstAirCreateSchema,
    OstAirusersPaginatedSchema,
    OstAiruserPaginatedSchema,
    OstTlscertificateCreateSchema,
    OstTlscertificateSchema,
    OstTlscertificatesPaginatedSchema,
    OstTlscertificatePaginatedSchema,
    OstsettingSchema,
    OstsettingEditSchema,
    OstsettingPaginatedSchema,
    OstBasicStatisticsSchema,
    OstAccentStatisticsSchema,
    OstOptimizedDupStatisticsSchema,
    OstaccentstatsSchema
    ]
