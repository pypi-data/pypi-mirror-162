from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlDrivesPaginatedSchema, VtlMediatypesPaginatedSchema)

from infiniguard_api.controller.vtl.drive import (list_drives, list_mediatypes)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class VtlDrivesResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Drives
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
    @marshal_with(VtlDrivesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List VTL drives
        """
        response, code = list_drives(kwargs, request.values)
        return (response, code)

@ddoc
class VtlMediatypesResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Drives 
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
    @doc(params={'drive_type':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'HPLTO4',
                  'name': 'drive_type',
                  'required': True}
                 })
    @marshal_with(VtlMediatypesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List VTL drives
        """
        kwargs['drivetype'] = kwargs.pop('drive_type')
        response, code = list_mediatypes(kwargs, request.values)
        return (response, code)

vtl_drives_view_func = VtlDrivesResource.as_view('vtl_drives')
vtl_mediatypes_view_func = VtlMediatypesResource.as_view('vtl_mediatypes')

vtl_api.add_url_rule(
    'drives',
    view_func=vtl_drives_view_func,
    methods=['GET'])

vtl_api.add_url_rule(
    'drives/<string:drive_type>/mediatypes',
    view_func=vtl_mediatypes_view_func,
    methods=['GET'])
