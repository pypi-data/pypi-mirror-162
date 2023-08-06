from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlHostmappingSchema,
                                               VtlHostmappingCreateSchema,
                                               VtlHostmappingsPaginatedSchema,
                                               VtlHostmappingPaginatedSchema)

from infiniguard_api.controller.vtl.host_mapping import (create_hostmapping,
                                                        list_hostmappings,
                                                        update_hostmapping,
                                                        get_hostmapping,
                                                        delete_hostmapping)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class VtlHostmappingsResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: VTL Partitions & Media & Hostmapping
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
    @marshal_with(VtlHostmappingsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List VTL hostmappings
        """
        kwargs['vtlname'] = kwargs.pop('par_name')
        response, code = list_hostmappings(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(VtlHostmappingCreateSchema(exclude=('name',)))
    @marshal_with(VtlHostmappingPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create VTL hostmapping
        """
        kwargs['name'] = kwargs.pop('par_name')
        response, code = create_hostmapping(kwargs)
        return (response, code)

@ddoc
class VtlHostmappingResource(MethodResource):
    """
    :Methods: GET, PUT, DELETE
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'ICICI-test',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'group_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'test_group',
                  'name': 'group_name',
                  'required': True}
                 })
    @marshal_with(VtlHostmappingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get VTL hostmapping
        """
        kwargs['vtlname']  = kwargs.pop('par_name')
        kwargs['groupname']  = kwargs.pop('group_name')
        response, code = get_hostmapping(kwargs)
        return (response, code)

    @ddoc
    @use_kwargs(VtlHostmappingCreateSchema(exclude=("name","groupname","wwpn","target",)))
    @marshal_with(VtlHostmappingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Update VTL hostmapping
        """
        kwargs['name']  = kwargs.pop('par_name')
        kwargs['groupname']  = kwargs.pop('group_name')
        response, code = update_hostmapping(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'ICICI-test',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'group_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'test_group',
                  'name': 'group_name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove VTL hostmapping
        """
        kwargs['name']  = kwargs.pop('par_name')
        kwargs['groupname']  = kwargs.pop('group_name')
        response, code  = delete_hostmapping(kwargs)
        return (response, code)

vtl_hostmapping_view_func  = VtlHostmappingResource.as_view('vtl_hostmapping')
vtl_hostmappings_view_func = VtlHostmappingsResource.as_view('vtl_hostmappings')

vtl_api.add_url_rule(
    'partitions/<string:par_name>/hostmappings/',
    view_func=vtl_hostmappings_view_func,
    methods=['GET', 'POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/hostmappings/<string:group_name>',
    view_func=vtl_hostmapping_view_func,
    methods=['GET', 'PATCH', 'DELETE'])
