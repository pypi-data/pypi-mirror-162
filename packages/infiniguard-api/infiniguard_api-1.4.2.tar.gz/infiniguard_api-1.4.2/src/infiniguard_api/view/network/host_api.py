from infiniguard_api.common.messages import paginated_params_desc
from infiniguard_api.controller.network.host import create_or_update_host, retrieve_host
from flask_apispec import MethodResource, doc, marshal_with, use_kwargs
from infiniguard_api.model.network import HostResponse, HostSchema, HostCreateUpdate
from infiniguard_api.view.network.common import network_api
from infiniguard_api.model.base_schema import ErrorResponseSchema
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc


@ddoc
class HostResource(MethodResource):
    """
    :Methods: POST, GET
    :Tags: Network Hosts
    """

    @ddoc
    @doc(operationId='create_host')
    @use_kwargs(HostSchema)
    @marshal_with(HostCreateUpdate, code=http_code.ACCEPTED, description="HostCreateUpdate on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create host configuration
        """
        response, code = create_or_update_host(kwargs)
        return response, code

    @ddoc
    @doc(operationId='retrieve_host')
    @doc(params=paginated_params_desc)
    @marshal_with(HostResponse, code=http_code.OK, description="HostResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the host configuration
        """
        response, qualifier, code = retrieve_host(kwargs)
        return response, code

    @ddoc
    @doc(operationId='update_host')
    @use_kwargs(HostSchema)
    @marshal_with(HostCreateUpdate, code=http_code.ACCEPTED, description="HostCreateUpdate on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Update host configuration
        """
        response, code = create_or_update_host(kwargs, update=True)
        return response, code


host_view_func = HostResource.as_view('host')

network_api.add_url_rule('host/', view_func=host_view_func, methods=['POST', 'GET', 'PATCH'])
