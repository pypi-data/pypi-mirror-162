from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlHostSchema,
                                               VtlHostCreateSchema,
                                               VtlHostsPaginatedSchema,
                                               VtlHostPaginatedSchema)

from infiniguard_api.controller.vtl.host import (create_host,
                                                 list_hosts,
                                                 update_host,
                                                 get_host,
                                                 delete_host)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class VtlHostsResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: VTL Hosts
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
                  'required': False}})
    @marshal_with(VtlHostsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List VTL hosts
        """
        response, code = list_hosts(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(VtlHostCreateSchema)
    @marshal_with(VtlHostPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create VTL host
        """
        response, code = create_host(kwargs)
        return (response, code)

@ddoc
class VtlHostResource(MethodResource):
    """
    :Methods: GET, PUT, DELETE
    :Tags: VTL Hosts
    """
    @ddoc
    @doc(params={'host_wwpn':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'tets_host',
                  'name': 'host_wwpn',
                  'required': True}
                 })
    @marshal_with(VtlHostPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get VTL host
        """
        kwargs['wwpn']  = kwargs.pop('host_wwpn')
        response, code = get_host(kwargs)
        return (response, code)

    @ddoc
    @use_kwargs(VtlHostSchema(exclude=("wwpn","connection_status",)))
    @marshal_with(VtlHostPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Update VTL host
        """
        kwargs['wwpn']  = kwargs.pop('host_wwpn')
        response, code = update_host(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'host_wwpn':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'test_host',
                  'name': 'host_wwpn',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove VTL host
        """
        kwargs['wwpn']  = kwargs.pop('host_wwpn')
        response, code  = delete_host(kwargs)
        return (response, code)

vtl_host_view_func  = VtlHostResource.as_view('vtl_host')
vtl_hosts_view_func = VtlHostsResource.as_view('vtl_hosts')

vtl_api.add_url_rule(
    'hosts',
    view_func=vtl_hosts_view_func,
    methods=['GET', 'POST'])

vtl_api.add_url_rule(
    'hosts/<string:host_wwpn>',
    view_func=vtl_host_view_func,
    methods=['GET', 'PATCH', 'DELETE'])
