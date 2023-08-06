from marshmallow import Schema
from marshmallow.fields import Int, String, Boolean, List, Nested
from marshmallow import validate, ValidationError
from marshmallow.decorators import validates_schema
from infiniguard_api.model.base_schema import MessageSchema, PaginatedResponseSchema
from infiniguard_api.model import custom_fields


class NetworkToolsResolvSchema(Schema):
    search_domain = List(String(),
                         description='List of search domains',
                         example=['localhost', 'blah.net'])
    nameservers = List(custom_fields.IpAddress(),
                       description='List of DNS servers',
                       example=['8.8.8.8', '8.8.8.4'])


class NetworkToolsResolvSchemaResponse(MessageSchema):
    result = Nested(NetworkToolsResolvSchema, many=False,
                    description='NetworkToolsResolvSchemaResponse')


class NetworkToolsPingSchema(Schema):
    dst = String(required=True,
                 validate=validate.Length(min=1, max=255),
                 description='Destination IP/Hostname',
                 example='10.10.10.1')
    src = String(required=False,
                 validate=validate.Length(min=1, max=255),
                 description='Source IP/Hostname',
                 example='10.10.10.2')
    time = Int(
        required=False,
        validate=validate.Range(min=1, max=20),
        default=5,
        example=5
    )
    do_not_fragment = Boolean(
        description='Raise do_not_fragment flag',
        required=False,
        default=False,
        example=False
    )
    payload_size = Int(
        required=False,
        validate=validate.Range(min=1, max=10000),
        description='Ping payload size',
        default=56,
        example=56
    )


class NetworkToolsMtuSchema(Schema):
    dst = String(required=True,
                 validate=validate.Length(min=1, max=255),
                 description='Destination IP/Hostname',
                 example='10.10.10.1')
    src = String(required=False,
                 validate=validate.Length(min=1, max=255),
                 description='Source IP/Hostname',
                 example='10.10.10.2')


class NetworkToolsDigSchema(Schema):
    dst = String(required=True,
                 validate=validate.Length(min=1, max=255),
                 description='IP/hostname to perform dig',
                 example='server1')
    time = Int(
        required=False,
        validate=validate.Range(min=1, max=20),
        default=3,
        example=3
    )


class NetworkToolsTracerouteSchema(Schema):
    dst = String(required=True,
                 validate=validate.Length(min=1, max=255),
                 description='Destination IP/Hostname',
                 example='10.10.10.1')
    src = String(required=False,
                 validate=validate.Length(min=1, max=255),
                 description='Source IP/Hostname',
                 example='10.10.10.2')
    no_resolve = Boolean(
        description='Do not resolve hostnames',
        required=False,
        default=False,
        example=False
    )


class NetworkToolsIperfSchema(Schema):
    dst = String(required=True,
                 validate=validate.Length(min=1, max=255),
                 description='Destination IP/Hostname',
                 example='10.10.10.1')
    src = String(required=False,
                 validate=validate.Length(min=1, max=255),
                 description='Source IP/Hostname',
                 example='10.10.10.2')
    time = Int(
        required=False,
        validate=validate.Range(min=1, max=30),
        default=10,
        example=5
    )
    iperf_version = Int(
        required=False,
        validate=validate.OneOf([1, 3]),
        default=3,
        example=3
    )
    parallel = Int(
        required=False,
        validate=validate.Range(min=1, max=20),
        default=1,
        example=1
    )
    buffer_len = Int(
        required=False,
        validate=validate.Range(min=128, max=1024),
        default=128,
        example=128
    )
    reverse = Boolean(
        description='Run iperf in opposite direction',
        required=False,
        example=False
    )

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        if data.get('reverse', False):
            if data.get('iperf_version', 2) != 3:
                errors = {'reverse': ["iperf_version = 3 required for reverse"]}
                raise ValidationError(errors)


class NetworkToolsBondsSchema(Schema):
    bond_id = Int(
        required=False,
        validate=validate.Range(min=0),
        default=0,
        example=0
    )


class NetworkToolsInterfaceStatsSchema(Schema):
    rx_packets = Int()
    tx_packets = Int()
    rx_bytes = Int()
    tx_bytes = Int()
    rx_errors = Int()
    tx_errors = Int()
    rx_dropped = Int()
    tx_dropped = Int()
    collisions = Int()
    rx_length_errors = Int()
    rx_over_errors = Int()
    rx_crc_errors = Int()
    tx_aborted_errors = Int()
    tx_carrier_errors = Int()


class NetworkToolsInterfaceEthtoolLinkModeSchema(Schema):
    autoneg = Boolean()
    duplex = String()
    speed = Int()
    supported_modes = List(String())
    supported_ports = List(String())


class NetworkToolsBondAdInfo(Schema):
    bond_ad_info_aggregator = Int()
    bond_ad_info_num_ports = Int()
    bond_ad_info_actor_key = Int()
    bond_ad_info_partner_key = Int()
    bond_ad_info_partner_mac = String()


class NetworkToolsBondInterface(NetworkToolsBondsSchema):
    bond_mode = Int()
    bond_active_slave = String()
    bond_miimon = Int()
    bond_updelay = Int()
    bond_downdelay = Int()
    bond_use_carrier = Int()
    bond_arp_interval = Int()
    bond_arp_validate = Int()
    bond_arp_all_targets = Int()
    bond_primary = Int()
    bond_primary_reselect = Int()
    bond_fail_over_mac = Int()
    bond_xmit_hash_policy = Int()
    bond_resend_igmp = Int()
    bond_num_peer_notif = Int()
    bond_all_slaves_active = Int()
    bond_min_links = Int()
    bond_lp_interval = Int()
    bond_packets_per_slave = Int()
    bond_ad_lacp_rate = Int()
    bond_ad_select = Int()
    bond_ad_actor_sys_prio = Int()
    bond_ad_user_port_key = Int()
    bond_tlb_dynamic_lb = Int()
    bond_ad_info = Nested(NetworkToolsBondAdInfo)
    bond_ports = List(String())


class NetworkToolsInterfaceAddress(Schema):
    intfname = String()
    address = String()
    broadcast = String()
    prefixlen = Int()


class NetworkToolsInterfaceRoutes(Schema):
    dst = String()
    dst_len = Int()
    gateway = String()
    family = Int()
    prefsrc = String()
    proto = Int()
    table = Int()
    type = Int()


class NetworkToolsInterfaceSchema(Schema):
    ifname = String()
    state = String()
    index = Int()
    operstate = String()
    carrier = Int()
    carrier_changes = Int()
    proto_down = Int()
    promiscuity = Int()
    kind = String()
    mtu = Int()
    hw_addr = String()
    phys_port_id = String()
    txqlen = Int()
    master = String()
    flags = Int()
    stats = Nested(NetworkToolsInterfaceStatsSchema)
    autoneg = Boolean()
    duplex = String()
    speed = Int()
    supported_modes = List(String())
    supported_ports = String()
    backend_port = Boolean()
    bond_properties = Nested(NetworkToolsBondInterface)
    ip_aliases = List(Nested(NetworkToolsInterfaceAddress))
    ip_routes = List(Nested(NetworkToolsInterfaceRoutes))
    vlan_id = Int()
    vlan_protocol = Int()


class NetworkToolsInterfaceSchemaResponse(MessageSchema):
    result = Nested(NetworkToolsInterfaceSchema, many=False,
                    description='NetworkToolsInterfaceSchema')


class NetworkToolsInterfacesSchemaResponse(PaginatedResponseSchema):
    result = Nested(NetworkToolsInterfaceSchema, many=True,
                    description='List of BondSchema')
