from infiniguard_api.lib.flask_apispec_override.wrappers import use_kwargs, marshal_with, doc, MethodResource
from flask import Blueprint

from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema
from infiniguard_api.model.node_schemas import (NodePingSchema,
                                                NodeIfconfigSchema,
                                                NodeMtuSchema,
                                                NodeNslookupSchema,
                                                NodeTracerouteSchema,
                                                NodeIperfSchema,
                                                NodeBondsSchema,
                                                NodeEthtoolSchema)
from infiniguard_api.model.task_schemas import (TaskSchema)

from infiniguard_api.controller.network.utils import (ping,
                                                      ifconfig,
                                                      mtu,
                                                      nslookup,
                                                      resolv,
                                                      traceroute,
                                                      iperf,
                                                      bonds,
                                                      ethtool)
from infiniguard_api.lib.rest.common import fill_responses, http_code
from infiniguard_api.lib.documentation import ddoc

network_utils_api = Blueprint('network_utils_api', __name__)
log = iguard_logging.get_logger(__name__)


@ddoc
class PingResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodePingSchema)
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
class IfconfigResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeIfconfigSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Get ifconfig data from DDE node
        :Description: Get ifconfig information from DDE node
        """
        response, code = ifconfig(**kwargs)
        return response, code


@ddoc
class MtuResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeMtuSchema)
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
class NslookupResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeNslookupSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Get ifconfig data from DDE node
        :Description: Get ifconfig information from DDE node
        """
        response, code = nslookup(**kwargs)
        return response, code


@ddoc
class ResolvResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
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
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeTracerouteSchema)
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
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeIperfSchema)
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
class ProcBondsResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeBondsSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Get bonds information
        :Description: Display contents of /proc/net/bonding/bond<bond_id>
        """
        response, code = bonds(**kwargs)
        return response, code


@ddoc
class EthtoolResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @doc(responses=fill_responses(ErrorResponseSchema()))
    @doc(responses=fill_responses(TaskSchema(), code=http_code.ACCEPTED))
    @use_kwargs(NodeEthtoolSchema)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Get ethtool information
        :Description: Display ethtool for interface(s)
        """
        response, code = ethtool(**kwargs)
        return response, code


ping_view_func = PingResource.as_view('ping')
ifconfig_view_func = IfconfigResource.as_view('ifconfig')
mtu_view_func = MtuResource.as_view('mtu')
nslookup_view_func = NslookupResource.as_view('nslookup')
resolv_view_func = ResolvResource.as_view('resolv')
traceroute_view_func = TracerouteResource.as_view('traceroute')
iperf_view_func = IperfResource.as_view('iperf')
bonds_view_func = ProcBondsResource.as_view('bonds')
ethtool_view_func = EthtoolResource.as_view('ethtool')


network_utils_api.add_url_rule(
    'ping',
    view_func=ping_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'ifconfig',
    view_func=ifconfig_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'mtu',
    view_func=mtu_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'nslookup',
    view_func=nslookup_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'resolv',
    view_func=resolv_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'traceroute',
    view_func=traceroute_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'iperf',
    view_func=iperf_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'bonds',
    view_func=bonds_view_func,
    methods=['POST'])

network_utils_api.add_url_rule(
    'ethtool',
    view_func=ethtool_view_func,
    methods=['POST'])
