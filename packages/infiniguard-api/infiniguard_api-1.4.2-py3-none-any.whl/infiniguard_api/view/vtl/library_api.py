from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlLibrariesPaginatedSchema)

from infiniguard_api.controller.vtl.library import (list_libraries)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class VtlLibrariesResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Libraries
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
    @marshal_with(VtlLibrariesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List VTL libraries
        """
        response, code = list_libraries(kwargs, request.values)
        return (response, code)

vtl_libraries_view_func = VtlLibrariesResource.as_view('vtl_libraries')

vtl_api.add_url_rule(
    'libraries',
    view_func=vtl_libraries_view_func,
    methods=['GET'])
