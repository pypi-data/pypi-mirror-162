from marshmallow import Schema
from marshmallow.fields import String, Nested, Int, Boolean
from marshmallow import validate, ValidationError, post_load
from marshmallow.decorators import validates_schema
from infiniguard_api.model.base_schema import PaginatedResponseSchema, NonPaginatedResponseSchema


class NasShareCommonSchema(Schema):
    hidden = Boolean(
        description='CIFS/SMB shares only, whether to display the share name in the browser',
        example=False)
    squash = String(
        validate=validate.OneOf(['root', 'none']),
        description='NFS only, squashes (maps) NFS client users to a nobody user',
        example='root')


class NasShareGetSchema(NasShareCommonSchema):
    name = String(required=True,
                  description='NAS share name',
                  attribute='share_name',
                  example='NAS_TEST')
    protocol = String(required=True,
                      validate=validate.OneOf(['cifs', 'nfs', 'app_specific']),
                      description='NAS protocol type',
                      attribute='protocol',
                      example='nfs')
    description = String(description='Nas share description',
                         attribute='description',
                         example='nas share NAS_TEST')
    dedup = Boolean(
        description='Data deduplication is enabled',
        example=True)
    permissions = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Share permissions',
        attribute='permissions',
        example='rw')
    allow_links = Boolean(dump_only=True,
                          description='Enable/disable support of Hard link',
                          example=True)
    export_path = String(dump_only=True,
                         description='Nas share export path name',
                         example='/Q/shares/NAS_TEST')
    access_hosts = String(dump_only=True,
                          description='Allowed hosts',
                          example='Allowed hosts')
    access_users = String(dump_only=True,
                          description='Allowed Users',
                          example='Allowed users')
    commit = String(dump_only=True,
                    validate=validate.OneOf(['sync', 'async']),
                    description='NFS only, set up NFS shares to commit data synchronously or asynchronously',
                    example='sync')
    anonuid = String(
        description='NFS only, the anonymous user ID',
        attribute='anonymous_uid',
        example='4294967294')
    anongid = String(
        description='NFS only, the anonymous group ID',
        attribute='anonymous_gid',
        example='4294967294')


def validate_proto_input(data):
    proto = data.get('protocol', None)
    if proto:
        if proto != 'nfs':
            if data.get('squash', None) or data.get('anonuid', None) or data.get('anongid', None):
                raise ValidationError(
                    'Parameter for NFS only', 'squash, anonuid, anongid')
        if proto != 'cifs':
            if data.get('namecase', None) or data.get('restart', None) or data.get('hidden', None):
                raise ValidationError(
                    'Parameter for CIFS only', 'namecase, restart, hidden')


class NasShareCreateSchema(NasShareCommonSchema):
    name = String(required=True,
                  description='NAS share name',
                  example='NAS_TEST')
    protocol = String(required=True,
                      validate=validate.OneOf(['cifs', 'nfs', 'app_specific']),
                      description='NAS protocol type',
                      example='nfs')
    description = String(description='Nas share description',
                         example='nas share NAS_TEST')
    dedup = Boolean(
        description='Data deduplication is enabled',
        example=True)
    permissions = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Share permissions',
        example='rw')
    anonuid = String(
        description='NFS only, the anonymous user ID',
        example='4294967294')
    anongid = String(
        description='NFS only, the anonymous group ID',
        example='4294967294')
    namecase = String(
        validate=validate.OneOf(['lower', 'default']),
        description='CIFS/SMB shares only, client file/directory names are stored using the specified character case',
        example='default')

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        validate_proto_input(data)


class NasShareEditSchema(NasShareCommonSchema):
    description = String(description='Nas share description',
                         example='nas share NAS_TEST')
    permissions = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Share permissions',
        example='rw')
    anonuid = String(
        description='NFS only, the anonymous user ID',
        example='4294967294')
    anongid = String(
        description='NFS only, the anonymous group ID',
        example='4294967294')
    namecase = String(
        validate=validate.OneOf(['lower', 'default']),
        description='CIFS/SMB shares only, client file/directory names are stored using the specified character case',
        example='default')
    restart = Boolean(
        description='CIFS/SMB shares only, restarts the CIFS/SMB service.',
        example=False)

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        validate_proto_input(data)

    @post_load
    def rename_fields(self, in_data, **kwargs):
        if in_data.get('description', None) is not None:
            in_data['desc'] = in_data.pop('description')
        if in_data.get('permissions', None) is not None:
            in_data['perms'] = in_data.pop('permissions')
        return in_data


class NfsSharehostCreateSchema(Schema):
    share = String(required=True,
                   description='NFS share name',
                   example='NAS_TEST')
    host = String(required=True,
                  description='host name',
                  example='172.20.44.198')
    permissions = String(missing='ro',
                         validate=validate.OneOf(['rw', 'ro']),
                         description='Share access permissions',
                         example='rw')


class NfsSharehostSchema(Schema):
    host = String(required=True,
                  description='host name',
                  attribute='host_name',
                  example='172.20.44.198')
    permissions = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Share access permissions',
        attribute='access_rights',
        example='rw')
    effective_perms = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Effective access permissions',
        attribute='effective_access_rights',
        example='rw')


class CifsShareuserCreateSchema(Schema):
    share = String(required=True,
                   description='NFS share name',
                   example='NAS_TEST')
    user = String(required=True,
                  description='user name',
                  example='user1')
    permissions = String(missing='ro',
                         validate=validate.OneOf(['rw', 'ro']),
                         description='Share access permissions',
                         example='rw')


class CifsShareuserSchema(Schema):
    user = String(required=True,
                  description='user name',
                  attribute='username',
                  example='user1')
    permissions = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Share access permissions',
        attribute='access_rights',
        example='rw')
    effective_perms = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Effective access permissions',
        attribute='effective_access_rights',
        example='rw')


class CifsShareadminSchema(Schema):
    user = String(required=True,
                  description='user name',
                  attribute='username',
                  example='user1')
    permissions = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Share access permissions',
        attribute='access_rights',
        example='rw')
    effective_perms = String(
        validate=validate.OneOf(['rw', 'ro']),
        description='Effective access permissions',
        attribute='effective_access_rights',
        example='rw')


class CifsAdsDomainCreateSchema(Schema):
    domain = String(required=True,
                    description='Name of the ADS domain to which to join the Samba server',
                    example='domain1')
    org = String(description='An organizational unit to assign to the domain',
                 example='orgA')
    admin = String(required=True,
                   description='ADS domain user that has to right to join the domain',
                   example='user1')
    password = String(required=True,
                      description='Domain user Password')
    pdc = String(description='Host name or IP address of the Primary Domain Controller',
                 example='host1')

    prewin2kdomain = String(description='The pre-Windows 2000 domain name',
                            example='netbios_name1')


class NfssettingSchema(Schema):
    nfssecure = Boolean(
        description='NFS seeting secure',
        example=True)


class NfssettingPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(NfssettingSchema,
                    many=False)


class SmbsettingEditSchema(Schema):
    serversigning = Boolean(
        description='Server signing setting',
        example=True)
    oplocks = Boolean(
        description='oplocks setting',
        example=True)

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        if data.get('serversigning', None) and data.get('oplocks', None):
            raise ValidationError(
                'serversigning, oplocks', 'mutually exclusive options')
        if not data.get('serversigning', None) and not data.get('oplocks', None):
            raise ValidationError(
                'serversigning, oplocks', 'valid options')


class SmbsettingSchema(Schema):
    server_signing = Boolean(
        description='Server signing setting',
        example=True)
    kernel_oplocks = Boolean(
        description='kernel oplocks setting',
        example=False)
    fake_kernel_oplocks = Boolean(
        description='fake kernel oplocks setting',
        example=False)
    oplocks = Boolean(
        description='oplocks setting',
        example=True)


class SmbsettingPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(SmbsettingSchema,
                    many=False)


class NasSharesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(NasShareGetSchema,
                    many=True)


class NasSharePaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(NasShareGetSchema(),
                    many=False)


class NfsSharesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(NasShareGetSchema, exclude=("hidden", "protocol",), partial=True,
                    many=True)


class NfsSharePaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(NasShareGetSchema, exclude=("hidden", "protocol",), partial=True,
                    many=False)


class NfsSharehostsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(NfsSharehostSchema,
                    many=True)


class NfsSharehostPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(NfsSharehostSchema,
                    many=False)


class CifsShareusersPaginatedSchema(PaginatedResponseSchema):
    result = Nested(CifsShareuserSchema,
                    many=True)


class CifsShareuserPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(CifsShareuserSchema(),
                    many=False)


class CifsShareadminsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(CifsShareadminSchema,
                    many=True)


class CifsShareadminPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(CifsShareadminSchema(),
                    many=False)


class CifsSharesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(NasShareGetSchema, exclude=("squash", "commit", "anonuid", "anongid", "protocol",), partial=True,
                    many=True)


class CifsSharePaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(NasShareGetSchema, exclude=("squash", "commit", "anonuid", "anongid", "protocol",), partial=True,
                    many=False)


class AppSpecificSharesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(NasShareGetSchema, exclude=("hidden", "squash", "commit", "anonuid", "anongid", "protocol",), partial=True,
                    many=True)


class AppSpecificSharePaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(NasShareGetSchema, exclude=("hidden", "squash", "commit", "anonuid", "anongid", "protocol",), partial=True,
                    many=False)


schema_classes = [
    NasShareCommonSchema,
    NasShareGetSchema,
    NasShareCreateSchema,
    NasShareEditSchema,
    NfsSharehostCreateSchema,
    NfsSharehostSchema,
    CifsShareuserCreateSchema,
    CifsShareuserSchema,
    CifsShareadminSchema,
    CifsAdsDomainCreateSchema,
    SmbsettingEditSchema,
    SmbsettingSchema,
    SmbsettingPaginatedSchema,
    NasSharesPaginatedSchema,
    NasSharePaginatedSchema,
    NfsSharesPaginatedSchema,
    NfsSharehostsPaginatedSchema,
    NfsSharehostPaginatedSchema,
    CifsShareusersPaginatedSchema,
    CifsShareuserPaginatedSchema,
    CifsShareadminsPaginatedSchema,
    CifsShareadminPaginatedSchema,
    CifsSharesPaginatedSchema,
    CifsSharePaginatedSchema,
    AppSpecificSharesPaginatedSchema,
    AppSpecificSharePaginatedSchema,
]
