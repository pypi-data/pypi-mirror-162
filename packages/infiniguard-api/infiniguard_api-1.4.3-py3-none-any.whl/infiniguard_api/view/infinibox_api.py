# -*- coding: utf-8 -*-
from flask_apispec import use_kwargs, marshal_with, doc, MethodResource
from flask import Blueprint, request
from marshmallow.fields import Int, String, List, Dict, Nested, Boolean, Field
from marshmallow import validate, Schema, missing

from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, PaginationSchema, ErrorSchema
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc
import os

infinibox_api = Blueprint('infinibox_api', __name__)
log = iguard_logging.get_logger(__name__)


class InfinidatUserSchema(Schema):
    password = String(example="123456", description="Password for the user")
    name = String(example="admin", description="User name")
    role_list = ["ADMIN", "POOL_ADMIN", "READ_ONLY"]
    if os.environ.get('OPENAPI_GEN'):
        role_list += ["INFINIDAT", "TECHNICIAN"]
    role = String(validate=validate.OneOf(role_list), example="ADMIN", description="User role")
    email = String(example="admin@infinidat.com", description="User email")


class DataSchema(Schema):
    type = String(required=True, validate=validate.OneOf(['int', 'string']))
    name = String(required=True, example='eventnum')
    value = String(required=True, example='1')


class UserDataSchema(Schema):
    type = String(example='Username')
    name = String(example='user_name')
    value = String(example='admin')


class InfiniboxReady(Schema):
    ready = Boolean(example=True)


class InfiniboxReadyPaged(InfiniboxReady):
    number_of_objects = Int(example=1)
    pages_total = Int(example=1)
    page = Int(example=1)
    page_size = Int(example=50)


class InfiniboxResponse(Schema):
    affected_entity_id = Int(example=0)
    username = String(example='infinidat')
    code = String(example='CUSTOM_INFO_EVENT')
    description = String(example='Some description')
    seq_num = Int(example=1, default=1)
    system_version = String(example="4.0.13.0-dev")
    reporter = String(example='CUSTOM')
    timestamp = Int(example=1531825334483)
    source_node_id = Int(example=1)
    id = Int(example=3195)


class InfiniboxResponseSchema(Schema):
    metadata = Nested(InfiniboxReady)
    error = String(default=None, example=None, allow_none=True)


class CustomEventSchema(Schema):
    description_template = String(required=True, example="Some description")
    data = Nested(DataSchema, many=True, example=[
        {
            "name": "eventnum",
            "type": "int",
            "value": "1"
        }
    ]
    )
    visibility = String(
        required=True, validate=validate.OneOf(['CUSTOMER', 'INFINIDAT']), example='CUSTOMER')
    level = String(required=True, validate=validate.OneOf(
        ['INFO', 'ERROR', 'WARNING', 'CRITICAL']), example='INFO')


class InfiniboxErrorResponseSchema(Schema):
    metadata = Dict(description="metadata such as pagination, sort etc",
                    example={"ready": True})
    error = Dict(description="error messages",
                 example={
                     "code": "AUTHENTICATION_REQUIRED",
                     "message": "You must authenticate"})
    result = Dict(example=None, allow_none=True)


class GetEventsResponseSchemaResult(InfiniboxResponse):
    code = String(example='USER_PASSWORD_UPDATED')
    description = String(
        example='Password for user \'admin\' has been updated')
    description_template = String(
        example="Password for user '{user_name}' has been updated")
    data = Nested(UserDataSchema, many=True)


class GetEventsResponseSchema(Schema):
    metadata = Nested(InfiniboxReadyPaged)
    result = Nested(GetEventsResponseSchemaResult, many=True)


class CustomEventSchemaInfiniboxResponse(CustomEventSchema, InfiniboxResponse):
    pass


class CustomEventResponseSchema(InfiniboxResponseSchema):
    result = Nested(CustomEventSchemaInfiniboxResponse)


class ExternalEventSchema(Schema):
    code = String(required=True, example="INFINIMETRICS_HEARTBEAT")


class ExternalEventSchemaInfiniboxResponse(ExternalEventSchema, InfiniboxResponse):
    description_template = String(example="INFINIMETRICS_HEARTBEAT")
    level = String(example='INFO')
    data = List(String(), default=[])
    visibility = String(example='INFINIDAT')


class ExternalEventResponseSchema(InfiniboxResponseSchema):
    result = Nested(ExternalEventSchemaInfiniboxResponse)


class DriveHWSchema(Schema):
    pending_reallocations = Int(example=10)
    state = String(example="OK")
    reallocations = Int(example=10)
    temperature = Int(example=10)
    power_on_hours = Int(example=10)


class DriveSchema(Schema):
    state_description = String(example="")
    drive_index = Int(example=1)
    vendor = String(example="vendor1")
    product_id = String(example="")
    enclosure_index = Int(example=1)
    firmware = String(example="n/a")
    hw = Nested(DriveHWSchema)
    probe_ttl = Int(example=86400000)
    failure_reason = String(example="REASON NONE")
    state = String(example="UNKNOWN")
    product_rev = String(example="")
    bytes_capacity = Int(example=0)
    serial_number = String(example="serial1")
    model = String(example="model1")
    last_probe_timestamp = Int(example=1390251656000)
    nodes_access = String(many=True, example=[False, False, False])
    id = Int(example=1)


class DriveResponseSchema(InfiniboxResponseSchema):
    result = Nested(DriveSchema)


class DrivesResponseSchema(Schema):
    metadata = Nested(InfiniboxReadyPaged)
    result = Nested(DriveSchema, many=True)


class DriveHWResposeSchema(InfiniboxResponseSchema):
    result = Nested(DriveHWSchema)


class EnclosureSchema(Schema):
    state_description = String(example="")
    vendor = String(example="NEWISYS")
    last_probe_timestamp = Int(example=1390254009000)
    firmware = String(example="0509")
    drives = Nested(DriveSchema, many=True)


class EnclosureResponseSchema(Schema):
    metadata = Nested(InfiniboxReadyPaged)
    result = Nested(EnclosureSchema, many=True)


class DdePort(Schema):
    port_num = Int(example=1, description="Port number on the patch panel")
    component_id = String(example="")
    conn_port_comp_id = String(
        example="DDE1FC5P4", description="Connection port component ID")
    conn_port_uuid = String(example="", description="Connection port UUID")
    label = String(example="FC5P4", description="Label as shown in the GUI")
    type = String(validate=validate.OneOf(
        ["FC", "ETH"]), example="FC", description="FC or Ethernet port type")
    media_type = String(validate=validate.OneOf(
        ["fiber", "copper"]), example="fiber", description="Media type - fibre or copper")
    hw_addr = String(example="50:0e:09:e2:00:15:01:13",
                     description="MAC address or WWPN of the port")
    state = String(example="OK", description="Port state")
    link_state = String(example="UP", description="Link state")
    connection_speed = Int(example=16000000000, description="Connection speed")


class DdeFrame(Schema):
    component_id = String(example="", description="Component ID")
    location = Int(example=1, description="Physical node location")
    label = String(example="DDE-Node 1",
                   description="Node label as shown in the GUI")
    color = String(example="red", description="Label color on patch panel/GUI")
    ports = Nested(DdePort, many=True)


class DdeFrames(Schema):
    frames = Nested(DdeFrame, many=True)


class DdeResponseSchema(InfiniboxResponseSchema):
    result = Nested(DdeFrames)


class DdeNodeState(Schema):
    health = String(example="NORMAL", description="Node health status")
    message = String(example="", description="Message regarding node health")
    lifecycle = String(example="ACTIVE", description="Node lifecycle")
    inline_performance = Int(
        example=110123, description="Current inline performance")
    total_disk_capacity = Int(example=10000000352256,
                              description="Total disk capacity")
    available_disk_capacity = Int(
        example=107374313472, description="Available disk capacity")
    used_disk_capacity = Int(
        example=3126151044, description="Used disk capacity")
    data_size_before_reduction = Int(
        example=6232292100, description="Data size before deduplication and compression")
    data_size_after_reduction = Int(
        example=404694292, description="Data size after deduplication and compression")
    total_reduction_ratio = String(
        example="15.4 : 1", description="Total deduplication ratio")
    is_metrics_data_stale = Boolean(
        example=False, description="Whether metrics data is stale")


class DdeNodeStatus(Schema):
    id = Int(example=18, description="Immutable, unique ID generated by MGMT")
    node_id = Int(example=1, description="Node ID")
    serial = String(example="AB34FF24324AC", description="Node serial number")
    color = String(example="red", description="Patch panel color")
    label = String(example="node-1", description="Node label")
    location = Int(example=1, description="Node location in the rack")
    dde_instance_id = Int(example=1, description="Node logical ID")
    dde_instance_ip = String(example="10.20.10.40",
                             description="DDE instance Internal IP")
    dde_instance_url = String(
        example="http://10.20.10.40/rest", description="DDE instance Internal URL")
    state = Nested(DdeNodeState)
    created_at = Int(example=1487679070211,
                     description="Resource creation timestamp")
    updated_at = Int(example=1487679076641,
                     description="Resource last update timestamp")


class DdeNodeStatusResponseSchema(InfiniboxResponseSchema):
    result = Nested(DdeNodeStatus)


class DdeNodesStatusResponseSchema(Schema):
    metadata = Nested(InfiniboxReadyPaged)
    result = Nested(DdeNodeStatus, many=True)


class InfinidatUserResult(InfinidatUserSchema):
    roles = List(String(), many=True, example=["ADMIN"], description="User roles")
    enabled = Boolean(example=True, description="Whether the user is enabled")
    id = Int(example=1704, description="System generated object ID")
    type = String(example="Local", description="User type")


class InfinidatUserDisabledResult(InfinidatUserResult):
    enabled = Boolean(example=False, description="Whether the user is enabled")


class InfinidatUserResponseSchema(InfiniboxResponseSchema):
    result = Nested(InfinidatUserResult, exclude=("password",))


class InfinidatUserResponseDisabledSchema(InfiniboxResponseSchema):
    result = Nested(InfinidatUserDisabledResult, exclude=("password",))


class InfinidatUsersResponseSchema(Schema):
    metadata = Nested(InfiniboxReadyPaged)
    result = Nested(InfinidatUserResult, exclude=("password",), many=True)


class InfinidatUserLogin(Schema):
    username = String(example='admin')
    password = String(example='password')


class InfinidatUserLoginSchema(Schema):
    user_objects = Nested(InfinidatUserResult,
        exclude=("password",), many=True)
    name = String(example='admin')
    roles = List(String(), many=True, example=["ADMIN"])


class InfinidatUserLoginResponse(InfiniboxResponseSchema):
    result = Nested(InfinidatUserLoginSchema)


class InfinidatSystemHealthState(Schema):
    rebuild_1_inprogress = Boolean(example=False)
    enclosure_failure_safe_distribution = Boolean(example=True)
    missing_drives = Int(example=0)
    inactive_nodes = Int(example=0)
    rebuild_2_inprogress = Boolean(example=False)
    active_cache_ssd_devices = Int(example=24)
    phasing_out_drives = Int(example=0)
    unknown_drives = Int(example=0)
    raid_groups_pending_rebuild_2 = Int(example=0)
    raid_groups_pending_rebuild_1 = Int(example=0)
    testing_drives = Int(example=0)
    ready_drives = Int(example=240)
    bbu_aggregate_charge_percent = Int(example=300)
    encryption_enabled = Boolean(example=True)
    active_drives = Int(example=240)
    failed_drives = Int(example=0)


class InfinidatSystemHealthStateResponse(InfiniboxResponseSchema):
    result = Nested(InfinidatSystemHealthState)


class InfinidatSystemNameResponse(InfiniboxResponseSchema):
    result = String(example='infiniguard236')


class LdapSchema(Schema):
    group_memberof_attribute = String(example="memberof")
    group_name_attribute = String(example="cn")
    groups_basedn = String(example="cn=users,dc=mgmt,dc=local")
    users_basedn = String(example="cn=users,dc=mgmt,dc=local")
    username_attribute = String(example="sAMAccountName")
    group_class = String(example="group")
    user_class = String(example="user")


class LdapSchemaPost(Schema):
    name = String(example="mgmt")
    schema_definition = Nested(LdapSchema, example={
        "group_class": "group",
        "group_memberof_attribute": "memberof",
        "group_name_attribute": "cn",
        "groups_basedn": "cn=users,dc=mgmt,dc=local",
        "user_class": "user",
        "username_attribute": "sAMAccountName",
        "users_basedn": "cn=users,dc=mgmt,dc=local"
    })
    bind_username = String(example="administrator")
    servers = String(example=None)
    domain_name = String(example="mgmt.local")
    bind_password = String(example="password")


class LdapSchemaResponse(LdapSchemaPost):
    bind_password = String(example=None)
    search_order = Int(example=0)
    ldap_port = Int(example=636)
    use_ldaps = Boolean(example=True)
    repository_type = String(example="ActiveDirectory")
    id = Int(example=1891)


class LdapSchemaResult(InfiniboxResponseSchema):
    result = Nested(LdapSchemaResponse)


class LdapsSchemaResult(InfiniboxResponseSchema):
    metadata = Nested(InfiniboxReadyPaged)
    result = Nested(LdapSchemaResponse, many=True)


@ddoc
class InfiniboxCustomEvent(MethodResource):
    """
    :Methods: POST
    :Tags: Events
    """
    @ddoc
    @use_kwargs(CustomEventSchema)
    @marshal_with(CustomEventResponseSchema, code=http_code.CREATED)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Create a custom event
        '''
        pass


@ddoc
class InfiniboxExternalEvent(MethodResource):
    """
    :Methods: POST
    :Tags: Events
    """
    @ddoc
    @use_kwargs(ExternalEventSchema)
    @marshal_with(ExternalEventResponseSchema, code=http_code.CREATED)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Create external event
        '''
        pass

    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(GetEventsResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get a sorted and filtered list of events
        '''
        pass


@ddoc
class InfiniboxDrive(MethodResource):
    """
    :Methods: GET
    :Tags: Racks
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @doc(params={'rackId':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'rackId',
                  'required': True}
                 })
    @doc(params={'enclosure_index':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'enclosure_index',
                  'required': True}
                 })
    @marshal_with(DriveResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get information about a specific drive by the enclosure ID and drive ID.
        '''
        pass


@ddoc
class InfiniboxDriveHW(MethodResource):
    """
    :Methods: GET
    :Tags: Racks
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @doc(params={'rackId':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'rackId',
                  'required': True}
                 })
    @doc(params={'enclosure_index':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'enclosure_index',
                  'required': True}
                 })
    @doc(params={'drive_index':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'drive_index',
                  'required': True}
                 })
    @marshal_with(DriveHWResposeSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get information about a specific drive HW by the enclosure ID and drive ID.
        '''
        pass


@ddoc
class InfiniboxDrives(MethodResource):
    """
    :Methods: GET
    :Tags: Racks
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @doc(params={'rackId':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'rackId',
                  'required': True}
                 })
    @doc(params={'enclosure_index':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'enclosure_index',
                  'required': True}
                 })
    @doc(params={'drive_index':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'drive_index',
                  'required': True}
                 })
    @marshal_with(DrivesResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get information about a specific drive by the enclosure ID and drive ID.
        '''
        pass


@ddoc
class InfiniboxEnclosure(MethodResource):
    """
    :Methods: GET
    :Tags: Racks
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @doc(params={'rackId':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'rackId',
                  'required': True}
                 })
    @marshal_with(EnclosureResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get information about enclosures.
        '''
        pass


@ddoc
class DdePatchPanels(MethodResource):
    """
    :Methods: GET
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(DdeResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get DDE patch panels information
        '''
        pass


@ddoc
class DdeNodeStatus(MethodResource):
    """
    :Methods: GET
    :Tags: DDE Nodes 
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @doc(params={'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1,
                  'name': 'id',
                  'required': True}
                 })
    @marshal_with(DdeNodeStatusResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get specific DDE node status
        '''
        pass


@ddoc
class DdeNodesStatus(MethodResource):
    """
    :Methods: GET
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(DdeNodesStatusResponseSchema, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        """
        :Summary: Get DDE nodes status

        """
        pass


@ddoc
class InfinidatUsersResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: Management Users
    """
    @ddoc
    @doc(params={'name':
                 {'in': 'query',
                  'description': 'User name',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(InfinidatUsersResponseSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        """
        :Summary: Get list of management users
        """
        pass

    @ddoc
    @use_kwargs(InfinidatUserSchema)
    @marshal_with(InfinidatUserResponseSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create management user
        """
        pass


@ddoc
class InfinidatUserByUsernameResource(MethodResource):
    """
    :Methods: GET
    :Tags: Management Users
    """
    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'description': 'User name',
                  'type': 'string',
                  'x-example': 'admin',
                  'required': True},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(InfinidatUsersResponseSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        """
        :Summary: Get a specific user by name
        """
        pass


@ddoc
class InfinidatUserLoginResource(MethodResource):
    """
    Methods: POST
    :Tags: Management Users
    """
    @ddoc
    @use_kwargs(InfinidatUserLogin)
    @marshal_with(InfinidatUserLoginResponse, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Login user account
        :Description: 
        InfiniBox supports both in-session and basic authentication.

        To start a new session, log into InfiniBox using: 

        ```
        POST /api/rest/users/login {"username": "jabba", "password": "the hut", "clientid": "optional client identifier"}
        ```

        Upon a successful login the client receives a cookie 

        ```
        {"Set-Cookie", "JSESSIONID=6977862313998501146;Version=1;Path=/"}
        ```

        Each subsequent request is authenticated with a cookie.

        To end the session, log out of InfiniBox using: 

        ```
        POST /api/rest/users/logout
        ```

        A User object looks like this:

        ```
        {"id": 17, "username": "sherlock", "email": "test@example.com", "role": "ADMIN"}
        ```

        Each user belongs to one of the following roles: Admin ,PoolAdmin or ReadOnly. 
        The ReadOnly role provides read-only access to the API. 
        The Admin and PoolAdmin roles provide read-write access.

        Note: user names are case-sensitive.
        '''
        pass


@ddoc
class InfinidatUserLogoutResource(MethodResource):
    """
    :Methods: POST
    :Tags: Management Users
    """
    @ddoc
    @marshal_with(InfinidatUserLoginResponse, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Logout user account
        :Description: 
        InfiniBox supports both in-session and basic authentication.

        To start a new session, log into InfiniBox using: 

        ```
        POST /api/rest/users/login {"username": "jabba", "password": "the hut", "clientid": "optional client identifier"}
        ```

        Upon a successful login the client receives a cookie 

        ```
        {"Set-Cookie", "JSESSIONID=6977862313998501146;Version=1;Path=/"}
        ```

        Each subsequent request is authenticated with a cookie.

        To end the session, log out of InfiniBox using: 

        ```
        POST /api/rest/users/logout
        ```

        A User object looks like this:

        ```
        {"id": 17, "username": "sherlock", "email": "test@example.com", "role": "ADMIN"}
        ```

        Each user belongs to one of the following roles: Admin ,PoolAdmin or ReadOnly. 
        The ReadOnly role provides read-only access to the API. 
        The Admin and PoolAdmin roles provide read-write access.

        Note: user names are case-sensitive.
        '''
        pass


@ddoc
class InfinidatUserDisableResource(MethodResource):
    """
    :Methods: POST
    :Tags: Management Users
    """
    @ddoc
    @doc(params={'id':
                 {'in': 'path',
                  'description': 'User ID',
                  'type': 'integer',
                  'x-example': '1704',
                  'required': True}
                 })
    @marshal_with(InfinidatUserResponseDisabledSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Disable user account
        '''
        pass


@ddoc
class InfinidatUserEnableResource(MethodResource):
    """
    :Methods: POST
    :Tags: Management Users
    """
    @ddoc
    @doc(params={'id':
                 {'in': 'path',
                  'description': 'User ID',
                  'type': 'integer',
                  'x-example': '1704',
                  'required': True}
                 })
    @marshal_with(InfinidatUsersResponseSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Enable user account
        '''
        pass


@ddoc
class InfinidatUserResource(MethodResource):
    """
    :Methods: GET, PUT, DELETE
    :Tags: Management Users
    """
    @ddoc
    @doc(params={'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1704,
                  'name': 'id',
                  'required': True,
                  'description': 'Numerical user ID'}
                 })
    @marshal_with(InfinidatUsersResponseSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get a specific user
        '''
        pass

    @doc(params={'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1704,
                  'name': 'id',
                  'required': True,
                  'description': 'Numerical user ID'}
                 })
    @ddoc
    @marshal_with(InfinidatUserResponseSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        '''
        :Summary: Delete a user
        '''
        pass

    @doc(params={'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1704,
                  'name': 'id',
                  'required': True,
                  'description': 'Numerical user ID'}
                 })
    @ddoc
    @use_kwargs(InfinidatUserSchema)
    @marshal_with(InfinidatUserResponseSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def put(self, **kwargs):
        '''
        :Summary: Modify user attribute
        '''
        pass


@ddoc
class InfiniboxSystemHealthState(MethodResource):
    """
    :Methods: GET
    :Tags: Health State
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(InfinidatSystemHealthStateResponse, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        """
        :Summary: Get information about InfiniBox status
        """
        pass


@ddoc
class InfiniboxSystemName(MethodResource):
    """
    :Methods: GET
    :Tags: System Configuration
    """
    @ddoc
    @doc(params={'filter':
                 {'in': 'query',
                  'description': 'field predicate and value for filter',
                  'type': 'string',
                  'required': False},
                 'sort':
                 {'in': 'query',
                  'description': 'list of fields to be sorted by',
                  'type': 'string',
                  'required': False},
                 'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @marshal_with(InfinidatSystemNameResponse, code=http_code.OK)
    @marshal_with(InfiniboxErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get system name
        '''
        pass


@ddoc
class InfinidatLdapsResource(MethodResource):
    """
    :Methods: POST, GET
    :Tags: System Configuration
    """
    @ddoc
    @use_kwargs(LdapSchemaPost)
    @marshal_with(LdapSchemaResult, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        '''
        :Summary: Create a repository of users whose members can log into InfiniBox
        '''
        pass

    @ddoc
    @marshal_with(LdapsSchemaResult, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get all of the repositories that are connected to InfiniBox
        '''
        pass


@ddoc
class InfinidatLdapResource(MethodResource):
    """
    :Methods: DELETE, GET, PUT
    :Tags: System Configuration
    """
    @doc(params={'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1891,
                  'name': 'id',
                  'required': True,
                  'description': 'Numerical LDAP repository ID'}
                 })
    @ddoc
    @marshal_with(LdapSchemaResult, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self):
        '''
        :Summary: Disconnect a repository from InfiniBox
        '''
        pass

    @doc(params={'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1891,
                  'name': 'id',
                  'required': True,
                  'description': 'Numerical LDAP repository ID'}
                 })
    @ddoc
    @marshal_with(LdapSchemaResult, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        '''
        :Summary: Get a repository that is connected to InfiniBox
        '''
        pass

    @doc(params={'id':
                 {'in': 'path',
                  'type': 'integer',
                  'x-example': 1891,
                  'name': 'id',
                  'required': True,
                  'description': 'Numerical LDAP repository ID'}
                 })
    @ddoc
    @use_kwargs(LdapSchemaPost)
    @marshal_with(LdapSchemaResult, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def put(self):
        '''
        :Summary: Update the repository definition
        '''
        pass


create_custom_event_view_func = InfiniboxCustomEvent.as_view('custom')
create_external_event_view_func = InfiniboxExternalEvent.as_view('external')
create_drive_view_func = InfiniboxDrive.as_view('drive')
create_drives_view_func = InfiniboxDrives.as_view('drives')
create_drive_hw_view_func = InfiniboxDrives.as_view('hw')
create_enclosure_view_func = InfiniboxEnclosure.as_view('enclosure')
create_patchpanel_view_func = DdePatchPanels.as_view('patchpanel')
create_status_view_func = DdeNodeStatus.as_view('status')
create_statuses_view_func = DdeNodeStatus.as_view('statuses')
create_users_view_func = InfinidatUsersResource.as_view('iboxusers')
create_user_view_func = InfinidatUserResource.as_view('iboxuser')
create_user_disable_view_func = InfinidatUserDisableResource.as_view(
    'iboxuser_disable')
create_user_enable_view_func = InfinidatUserEnableResource.as_view(
    'iboxuser_enable')
create_user_login_view_func = InfinidatUserLoginResource.as_view(
    'iboxuser_login')
create_user_logout_view_func = InfinidatUserLogoutResource.as_view(
    'iboxuser_logout')
create_user_by_username_view_func = InfinidatUserByUsernameResource.as_view(
    'iboxuser_by_username')
create_health_state_view_func = InfiniboxSystemHealthState.as_view(
    'healthstate')
create_system_name_view_func = InfiniboxSystemName.as_view('systemname')
create_ldap_view_func = InfinidatLdapResource.as_view('ldap')
create_ldaps_view_func = InfinidatLdapsResource.as_view('ldaps')

infinibox_api.add_url_rule(
    'events/custom',
    view_func=create_custom_event_view_func,
    methods=['POST'])
infinibox_api.add_url_rule(
    'events',
    view_func=create_external_event_view_func,
    methods=['POST', 'GET'])
infinibox_api.add_url_rule(
    'components/racks/<int:rackId>/enclosures/<int:enclosure_index>/drives/<int:drive_index>',
    view_func=create_drive_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'components/racks/<int:rackId>/enclosures/<int:enclosure_index>/drives',
    view_func=create_drives_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'components/racks/<int:rackId>/enclosures/<int:enclosure_index>/drives/<int:drive_index>/hw',
    view_func=create_drive_hw_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'components/racks/<int:rackId>/enclosures',
    view_func=create_enclosure_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'integrations/infiniguard/dde_nodes/patch_panels',
    view_func=create_patchpanel_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'integrations/infiniguard/dde_nodes/<int:id>',
    view_func=create_status_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'integrations/infiniguard/dde_nodes',
    view_func=create_statuses_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'users',
    view_func=create_users_view_func,
    methods=['GET', 'POST'])
infinibox_api.add_url_rule(
    'users/<int:id>',
    view_func=create_user_view_func,
    methods=['GET', 'PUT', 'DELETE'])
infinibox_api.add_url_rule(
    'users/<string:name>/by_username',
    view_func=create_user_by_username_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'users/<int:id>/disable',
    view_func=create_user_disable_view_func,
    methods=['POST'])
infinibox_api.add_url_rule(
    'users/<int:id>/enable',
    view_func=create_user_enable_view_func,
    methods=['POST'])
infinibox_api.add_url_rule(
    'users/login',
    view_func=create_user_login_view_func,
    methods=['POST'])
infinibox_api.add_url_rule(
    'users/logout',
    view_func=create_user_logout_view_func,
    methods=['POST'])
infinibox_api.add_url_rule(
    'system/health_state',
    view_func=create_health_state_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'system/name',
    view_func=create_system_name_view_func,
    methods=['GET'])
infinibox_api.add_url_rule(
    'config/ldap',
    view_func=create_ldaps_view_func,
    methods=['POST', 'GET'])
infinibox_api.add_url_rule(
    'config/ldap/<int:id>',
    view_func=create_ldap_view_func,
    methods=['DELETE', 'GET', 'PUT'])
