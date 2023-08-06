from infiniguard_api.model import custom_fields, validators
from infiniguard_api.model.base_schema import MessageSchema, PaginatedResponseSchema
from infiniguard_api.controller.network import host, interfaces
from marshmallow import Schema, ValidationError, post_load, pre_dump, validate, validates_schema
from marshmallow.fields import Boolean, Int, List, Nested, String


class HostSchema(Schema):
    hostname = String(description='DDE Host Name', example='host0')
    search_domain = List(String(required=True),
                         attribute='dns_search_path',
                         description='List of search domains',
                         example=['localhost', 'blah.net'])
    dns_servers = List(custom_fields.IpAddress(required=True),
                       description='List of DNS servers',
                       example=['8.8.8.8', '8.8.8.4'])
    # read only field, set it to interface gateway when ext_host_ip is set to YES
    # we do not handle error besides anything syscli returns
    default_gateway = custom_fields.IpAddress(attribute='default_gateway',
                                              description='Default gateway IP',
                                              example='10.10.10.1')


class HostCreateUpdateSchema(HostSchema):
    @post_load
    def convert_from_request(self, in_data, **kwargs):
        host.convert_from_request(in_data)
        if in_data.get('default_gateway', None) and in_data['default_gateway'] is not None:
            raise ValidationError(
                'Default Gateway is automatically set from an interface gateway with ext_host_ip as YES')
        return in_data

    @pre_dump
    def convert_to_response(self, out_data, **kwargs):
        return host.convert_to_response(out_data)


class HostResponseSchema(Schema):
    hostname = String(description='DDE Host Name', example='host0')
    search_domain = List(String(),
                         attribute='dns_search_path',
                         description='List of search domains',
                         example=['localhost', 'blah.net'])
    dns_servers = List(String(),
                       description='List of DNS servers',
                       example=['8.8.8.8', '8.8.8.4'])
    # read only field, set it to interface gateway when ext_host_ip is set to YES
    # we do not handle error besides anything syscli returns
    default_gateway = String(attribute='default_gateway',
                             description='Default gateway IP',
                             example='10.10.10.1')


class HostResponse(MessageSchema):
    result = Nested(HostResponseSchema)

    @pre_dump
    def convert_to_response(self, out_data, **kwargs):
        result = host.convert_to_response(out_data.get('result', {}))
        out_data['result'] = result
        return out_data


class HostCreateUpdate(MessageSchema):
    result = Nested(HostCreateUpdateSchema)


class StaticRouteSchema(Schema):
    network = custom_fields.IpAddress(required=True,
                                      description='Destination network',
                                      example='10.10.10.0')
    mask = custom_fields.Netmask(attribute='netmask',
                                 required=True,
                                 description='Destination netmask',
                                 example='255.255.255.0')
    gateway = custom_fields.IpAddress(
        required=True, description='Gateway IP address', example='10.10.10.1')
    devname = String(description='Device Name', example='dev0')


class StaticRouteResponse(MessageSchema):
    result = Nested(StaticRouteSchema)


class StaticRoutesResponse(PaginatedResponseSchema):
    result = List(Nested(StaticRouteSchema),
                  example=[
        {
            "gateway": "10.10.10.1",
            "mask": "255.255.255.0",
            "network": "10.10.10.0"
        }
    ])


class DeviceSchema(Schema):
    devname = String(attribute='Name', required=True,
                     description='Device Name', example='dev0')
    max_speed = String(attribute='MaxSpeed', required=True,
                       description='Maximum Speed', example='10GbE')
    intf_names = List(String(), dump_only=True,
                      description='List of interface names',
                      example=['dev0', 'dev1'],
                      allow_none=True)


class DeviceResponse(MessageSchema):
    result = Nested(DeviceSchema, only=['devname', 'max_speed'])


class DevicesResponse(PaginatedResponseSchema):
    result = List(Nested(DeviceSchema, only=['devname', 'max_speed']),
                  example=[
        {
            "devname": "p4p1",
            "max_speed": "10GbE"
        }
    ])


class InterfaceSchema(Schema):
    intfname = String(validate=validators.validate_intfname, description='Interface Name',
                      example='dev0.2:1')
    ip_address = custom_fields.IpAddress(
        description='IP Address', example='10.10.10.10')
    netmask = custom_fields.Netmask(
        description='Netmask', example='255.255.255.0')
    gateway = custom_fields.IpAddress(
        description='Gateway', example='10.10.10.1')

    segments = List(String(validate=validate.OneOf(['REP', 'MGMT', 'DATA', 'ALL']),
                           description='Which segments are allowed on the interface'), example='ALL')
    mtu = Int(validate=validate.Range(min=68, max=9192),
              description='MTU for the interface', example=1500)

    ext_host_ip = Boolean(
        description='Whether or not this is the default DDE interface', example=True)
    nat = custom_fields.IpAddress(description='NAT IP address')
    type = String(validate=validate.OneOf(['Port', 'Bond']), dump_only=True)

    operstate = String(validate=validate.OneOf(['UP', 'DOWN', 'up', 'down']), dump_only=True,
                       description='Interface operational state')
    carrier = String(validate=validate.OneOf(['UP', 'DOWN', 'up', 'down']), dump_only=True,
                     description='Interface link status')
    configured = Boolean(dump_only=True, description='Whether the interface has been configured',
                         example=False)
    routes = List(Nested(StaticRouteSchema), dump_only=True,
                  description='Routes for the interface', example=0)
    devname = String(validate=validate.Regexp(r'^[a-z0-9]+\Z'), dump_only=True,
                     description='Device name', example='dev0')

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        if self.only:
            if not set(data).issubset(set(self.only)):
                raise ValidationError("Only ['ipaddr', 'netmask', 'gateway', 'segments', 'mtu', 'nat', 'ext_host_ip' "
                                      "can be modified.")
            return

        if not data.get('intfname', None):
            raise ValidationError("'intfname' not specified.")

        if not all(k in data for k in ("ip_address", "netmask", "gateway")):
            raise ValidationError(
                '{ip_address, netmask, gateway} must all be provided.')
        # if data.get('ext_host_ip') and data.get('segments') not in ['MGMT', 'ALL']:
        #     raise ValidationError("'segments' must either MGMT or ALL if 'ext_host_ip' is YES.")

    @post_load
    def convert_in(self, in_data, **kwargs):
        return interfaces.convert_from_request(in_data)


class InterfaceResponse(MessageSchema):
    result = Nested(InterfaceSchema)


class InterfacesResponse(PaginatedResponseSchema):
    result = List(Nested(InterfaceSchema),
                  example=[
        {
            "carrier": "up",
            "configured": True,
            "default_gateway": "NO",
            "devname": "p4p4",
            "ext_host_ip": "YES",
            "gateway": "172.20.63.254",
            "intfname": "p4p4:1",
            "ip_address": "172.20.45.226",
            "mtu": 1500,
            "netmask": "255.255.224.0",
            "operstate": "up",
            "segments": [
                "ALL"
            ],
            "type": "Port"
        }])


class BondCreateSchema(InterfaceSchema):
    mode = String(validate=validate.OneOf(
        ['rr', 'ab', 'lacp', 'RR', 'AB', 'LACP']), description='Bond mode', example='lacp')
    slave_names = List(String,
                       validate=validators.validate_slaves,
                       description='List of bond slaves',
                       example=['dev0', 'dev1'])
    type = String(validate=validate.OneOf(
        ['bond']), dump_only=True, example='bond')

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        if not data.get('slave_names', None) and not data.get('mode', None):
            raise ValidationError(
                'either slave_names or mode is required to update a bond.')
        if self.only:
            return
        if not data.get('slave_names', None) or not data.get('mode', None):
            raise ValidationError(
                'both slave_names and mode are required to create a bond.')
        super(BondCreateSchema, self)._validates_schema(data)

    @post_load
    def convert_in(self, in_data, **kwargs):
        if not in_data:
            return
        if in_data.get('slave_names', None):
            in_data['slaves'] = ','.join(in_data.pop('slave_names'))
        if self.only:
            return in_data
        super(BondCreateSchema, self).convert_in(in_data)
        return(in_data)


class BondSchema(Schema):
    devname = String(required=True, description='Device name', example='bond0')
    type = String(validate=validate.OneOf(
        ['bond', 'Bond']), dump_only=True, example='Bond')
    slave_names = List(String(required=True),
                       required=True,
                       validate=validators.validate_slaves,
                       description='List of bond slave interfaces', example=['dev0', 'dev1'])
    mode = String(required=True, description='Bond mode', example='RR')
    mtu = Int(validate=validate.Range(min=68, max=9192),
              description='MTU for the interface', example=1500)
    configured = Boolean(dump_only=True,
                         description='Whether or not the interface has been configured',
                         example=True)


class BondResponse(MessageSchema):
    result = Nested(BondSchema, description='BondSchema')


class BondsResponse(PaginatedResponseSchema):
    result = List(Nested(BondSchema),
                  description='List of BondSchema',
                  example=[{
                      "configured": True,
                      "devname": "bond0",
                      "mtu": 1500,
                      "slave_names": [
                          "p7p2",
                          "p7p3"
                      ],
                      "type": "Bond"
                  }])


schema_classes = [
    HostSchema,
    HostResponse,
    HostCreateUpdate,
    StaticRouteSchema,
    StaticRouteResponse,
    StaticRoutesResponse,
    DeviceSchema,
    DeviceResponse,
    DevicesResponse,
    InterfaceSchema,
    InterfaceResponse,
    InterfacesResponse,
    BondCreateSchema,
    BondSchema,
    BondResponse,
    BondsResponse
]
