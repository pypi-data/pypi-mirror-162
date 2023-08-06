from schematics.types import StringType, IntType, BooleanType
from schematics.types.compound import ListType, ModelType, PolyModelType
from schematics.exceptions import ValidationError

from infiniguard_api.model.base_schema import DataModel as Model, APIModel

USER_ROLES = ['backupuser', 'airuser']


class UserModel(Model):
    name = StringType(required=True, deserialize_from='username')
    password = StringType()
    description = StringType()
    role = StringType(required=True, default=USER_ROLES[0],
                      choices=USER_ROLES)
    admin = BooleanType(serialize_when_none=False)


class MetadataModel(APIModel):
    page_size = IntType(serialize_when_none=False)
    page = IntType(serialize_when_none=False)
    pages_total = IntType(serialize_when_none=False)
    number_of_objects = IntType(serialize_when_none=False)
    ready = BooleanType(default=True, required=True, serialize_when_none=True)


class ErrorModel(APIModel):
    code = StringType()
    message = StringType()


class BaseResponseModel(APIModel):
    metadata = ModelType(
        MetadataModel, serialize_when_none=True, default=MetadataModel)
    error = ModelType(ErrorModel)


class ListResponseModel(BaseResponseModel):
    result = ListType(PolyModelType([UserModel, ]))


class EntityResponseModel(BaseResponseModel):
    result = PolyModelType([UserModel, ])


class EmptyResponseModel(BaseResponseModel):
    result = BooleanType(default=True)


class NetworkToolsResolvModel(Model):
    nameservers = ListType(StringType())
    search_domain = ListType(StringType())


class NetworkToolsInterfaceStats(Model):
    rx_packets = IntType()
    tx_packets = IntType()
    rx_bytes = IntType()
    tx_bytes = IntType()
    rx_errors = IntType()
    tx_errors = IntType()
    rx_dropped = IntType()
    tx_dropped = IntType()
    collisions = IntType()
    rx_length_errors = IntType()
    rx_over_errors = IntType()
    rx_crc_errors = IntType()
    tx_aborted_errors = IntType()
    tx_carrier_errors = IntType()


class NetworkToolsInterfaceEthtoolLinkMode(Model):
    autoneg = BooleanType()
    duplex = StringType()
    speed = IntType()
    supported_modes = ListType(StringType())
    supported_ports = ListType(StringType())


class NetworkToolsBondAdInfo(Model):
    bond_ad_info_aggregator = IntType(
        deserialize_from='IFLA_BOND_AD_INFO_AGGREGATOR')
    bond_ad_info_num_ports = IntType(
        deserialize_from='IFLA_BOND_AD_INFO_NUM_PORTS')
    bond_ad_info_actor_key = IntType(
        deserialize_from='IFLA_BOND_AD_INFO_ACTOR_KEY')
    bond_ad_info_partner_key = IntType(
        deserialize_from='IFLA_BOND_AD_INFO_PARTNER_KEY')
    bond_ad_info_partner_mac = StringType(
        deserialize_from='IFLA_BOND_AD_INFO_PARTNER_MAC')


class NetworkToolsBondInterface(Model):
    bond_mode = IntType()
    bond_active_slave = IntType()
    bond_miimon = IntType()
    bond_updelay = IntType()
    bond_downdelay = IntType()
    bond_use_carrier = IntType()
    bond_arp_interval = IntType()
    bond_arp_validate = IntType()
    bond_arp_all_targets = IntType()
    bond_primary = IntType()
    bond_primary_reselect = IntType()
    bond_fail_over_mac = IntType()
    bond_xmit_hash_policy = IntType()
    bond_resend_igmp = IntType()
    bond_num_peer_notif = IntType()
    bond_all_slaves_active = IntType()
    bond_min_links = IntType()
    bond_lp_interval = IntType()
    bond_packets_per_slave = IntType()
    bond_ad_lacp_rate = IntType()
    bond_ad_select = IntType()
    bond_ad_actor_sys_prio = IntType()
    bond_ad_user_port_key = IntType()
    bond_tlb_dynamic_lb = IntType()
    bond_ad_info = ModelType(NetworkToolsBondAdInfo)
    bond_ports = ListType(StringType())


class NetworkToolsInterfaceAddress(Model):
    intfname = StringType(deserialize_from='label')
    address = StringType()
    broadcast = StringType()
    prefixlen = IntType()


class NetworkToolsInterfaceRoutes(Model):
    dst = StringType()
    dst_len = IntType()
    gateway = StringType()
    family = IntType()
    prefsrc = StringType()
    proto = IntType()
    table = IntType()
    type = IntType()


class NetworkToolsInterface(Model):
    ifname = StringType()
    index = IntType()
    state = StringType()
    operstate = StringType()
    carrier = IntType()
    carrier_changes = IntType()
    proto_down = IntType()
    promiscuity = IntType()
    kind = StringType()
    mtu = IntType()
    hw_addr = StringType(deserialize_from='address')
    phys_port_id = StringType()
    txqlen = IntType()
    master = StringType()
    flags = IntType()
    stats = ModelType(NetworkToolsInterfaceStats)
    autoneg = BooleanType()
    duplex = StringType()
    speed = IntType()
    supported_modes = ListType(StringType())
    supported_ports = StringType()
    backend_port = BooleanType(default=False)
    bond_properties = ModelType(NetworkToolsBondInterface)
    ip_aliases = ListType(ModelType(NetworkToolsInterfaceAddress))
    ip_routes = ListType(ModelType(NetworkToolsInterfaceRoutes))
    vlan_id = IntType()
    vlan_protocol = IntType()
