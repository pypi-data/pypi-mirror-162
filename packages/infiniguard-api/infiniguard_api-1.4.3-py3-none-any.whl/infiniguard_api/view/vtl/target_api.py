from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlTargetsPaginatedSchema)

from infiniguard_api.controller.vtl.target import (list_targets)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class VtlTargetsResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Targets
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
    @marshal_with(VtlTargetsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List VTL targets
        """
        response, code = list_targets(kwargs, request.values)
        return (response, code)

vtl_targets_view_func = VtlTargetsResource.as_view('vtl_targets')

vtl_api.add_url_rule(
    'targets',
    view_func=vtl_targets_view_func,
    methods=['GET'])
