from infiniguard_api.common.messages import paginated_params_desc
from infiniguard_api.controller.network.interfaces import (create_interface,
                                                           delete_interface,
                                                           retrieve_interface,
                                                           update_interface)
from flask_apispec import (MethodResource,
                           doc,
                           marshal_with,
                           use_kwargs)
from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema
from infiniguard_api.model.network import (InterfaceResponse,
                                           InterfaceSchema,
                                           InterfacesResponse)
from infiniguard_api.view.network.common import network_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc


@ddoc
class InterfacesResource(MethodResource):
    """
    :Methods: POST,GET
    :Tags: Network Interfaces

    """

    @ddoc
    @doc(operationId='create_interface')
    @use_kwargs(InterfaceSchema)
    @marshal_with(InterfaceResponse, code=http_code.ACCEPTED, description="InterfaceResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create interface
        """
        response, code = create_interface(kwargs)
        return response, code

    @ddoc
    @doc(operationId='retrieve_interfaces')
    @doc(params=paginated_params_desc)
    @marshal_with(InterfacesResponse, code=http_code.OK, description="InterfacesResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return all interfaces
        """
        response, qualifier, code = retrieve_interface(kwargs)
        return response, code


@ddoc
class InterfaceResource(MethodResource):
    """
    :Methods: GET,DELETE
    :Tags: Network Interfaces
    """

    @ddoc
    @doc(operationId='retrieve_interface')
    @doc(params=paginated_params_desc)
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4:1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(InterfaceResponse, code=http_code.OK, description="InterfaceResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return the specified interface
        """
        response, qualifier, code = retrieve_interface(kwargs)
        return response, code

    @ddoc
    @doc(operationId='update_interface')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4:1',
                  'name': 'name',
                  'required': True}
                 })
    @use_kwargs(InterfaceSchema(only=('ip_address', 'netmask', 'gateway', 'segments', 'mtu', 'nat', 'ext_host_ip')))
    @marshal_with(InterfaceResponse, code=http_code.ACCEPTED, description="InterfaceResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Update the interface configuration
        """
        response, code = update_interface(kwargs)
        return response, code

    @ddoc
    @doc(operationId='delete_interface')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4:1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete the interface with the specified name
        """
        response, code = delete_interface(**kwargs)
        return response, code


interfaces_view_func = InterfacesResource.as_view('interfaces')
interface_view_func = InterfaceResource.as_view('interface')
network_api.add_url_rule(
    'interfaces/', view_func=interfaces_view_func, methods=['POST', 'GET'])
network_api.add_url_rule('interfaces/<string:name>',
                         view_func=interface_view_func, methods=['GET', 'PATCH', 'DELETE'])
