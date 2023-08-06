from flask_apispec import use_kwargs, marshal_with, doc, MethodResource
from flask import Blueprint, request
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.model.base_schema import ErrorResponseSchema
from infiniguard_api.model.network_tools_schemas import (NetworkToolsPingSchema,
                                                         NetworkToolsMtuSchema,
                                                         NetworkToolsDigSchema,
                                                         NetworkToolsTracerouteSchema,
                                                         NetworkToolsIperfSchema,
                                                         NetworkToolsInterfacesSchemaResponse,
                                                         NetworkToolsResolvSchemaResponse)
from infiniguard_api.model.task_schemas import (TaskSchema)
from infiniguard_api.controller.network.tools import (ping,
                                                      mtu,
                                                      dig,
                                                      resolv,
                                                      traceroute,
                                                      iperf,
                                                      interfaces_details)
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

network_tools_api = Blueprint('network_tools_api', __name__)
log = iguard_logging.get_logger(__name__)


@ddoc
class PingResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Network Tools
    """
    @ddoc
    @use_kwargs(NetworkToolsPingSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Ping from DDE to external IP
        :Description: Ping external system from DDE.
        """
        response, code = ping(**kwargs)
        return response, code


@ddoc
class MtuResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Network Tools
    """
    @ddoc
    @use_kwargs(NetworkToolsMtuSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: MTU Discovery
        :Description: Discover MTU from DDE to external IP.
        """
        response, code = mtu(**kwargs)
        return response, code


@ddoc
class DigResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Network Tools
    """
    @ddoc
    @use_kwargs(NetworkToolsDigSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Get name lookup data from DDE node
        :Description: Get name lookup information from DDE node
        """
        response, code = dig(**kwargs)
        return response, code


@ddoc
class ResolvResource(MethodResource):
    """
    :Methods: GET
    :Tags: DDE Network Tools
    """
    @ddoc
    @marshal_with(NetworkToolsResolvSchemaResponse, code=http_code.OK, description="ResolvSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: resolv.conf
        :Description: Display the contents of /etc/resolv.conf
        """
        response, code = resolv(**kwargs)
        return response, code


@ddoc
class TracerouteResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Network Tools
    """
    @ddoc
    @use_kwargs(NetworkToolsTracerouteSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Ping from DDE to external IP
        :Description: Ping external system from DDE.
        """
        response, code = traceroute(**kwargs)
        return response, code


@ddoc
class IperfResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Network Tools
    """
    @ddoc
    @use_kwargs(NetworkToolsIperfSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Run iperf client
        :Description: Run iperf client from DDE to station/server
        """
        response, code = iperf(**kwargs)
        return response, code


@ddoc
class InterfacesDetailsResource(MethodResource):
    """
    :Methods: GET
    :Tags: DDE Network Tools
    """

    @ddoc
    @doc(operationId='network_interfaces_details')
    @doc(params={'name':
                 {'in': 'query',
                  'type': 'string',
                  'description': 'Interface name',
                  'x-example': 'p4p1',
                  'name': 'name',
                  'required': False},
                 'backend_ports':
                 {'in': 'query',
                  'type': 'boolean',
                  'description': 'Show backend interfaces',
                  'x-example': 'true',
                  'name': 'backend_ports',
                  'required': False}})
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
                  'required': False}})
    @marshal_with(NetworkToolsInterfacesSchemaResponse, code=http_code.OK, description="InterfaceResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return network interfaces details
        """
        response, code = interfaces_details(request.values, **kwargs)
        return response, code


ping_view_func = PingResource.as_view('ping')
mtu_view_func = MtuResource.as_view('mtu')
dig_view_func = DigResource.as_view('dig')
resolv_view_func = ResolvResource.as_view('resolv')
traceroute_view_func = TracerouteResource.as_view('traceroute')
iperf_view_func = IperfResource.as_view('iperf')
interface_details_view_func = InterfacesDetailsResource.as_view(
    'interface_details')

network_tools_api.add_url_rule(
    'ping',
    view_func=ping_view_func,
    methods=['POST'])


network_tools_api.add_url_rule(
    'mtu',
    view_func=mtu_view_func,
    methods=['POST'])

network_tools_api.add_url_rule(
    'dig',
    view_func=dig_view_func,
    methods=['POST'])

network_tools_api.add_url_rule(
    'resolv',
    view_func=resolv_view_func,
    methods=['GET'])

network_tools_api.add_url_rule(
    'traceroute',
    view_func=traceroute_view_func,
    methods=['POST'])

network_tools_api.add_url_rule(
    'iperf',
    view_func=iperf_view_func,
    methods=['POST'])

network_tools_api.add_url_rule(
    'interface_details',
    view_func=interface_details_view_func,
    methods=['GET'])
