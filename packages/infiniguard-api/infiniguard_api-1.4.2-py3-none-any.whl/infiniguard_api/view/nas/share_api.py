from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.nas_schemas import (NasShareCreateSchema,
                                               NasShareEditSchema,
                                               NasSharesPaginatedSchema,
                                               NasSharePaginatedSchema)

from infiniguard_api.controller.nas.share import (create_share,
                                                  list_shares,
                                                  update_share,
                                                  delete_shares,
                                                  delete_share,
                                                  get_share)

from flask import request

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

PROTOCOLS = ['nfs', 'cifs','app_specific']

@ddoc
class SharesResource(MethodResource):
    """
    :Methods: GET, POST, DELETE
    :Tags: NAS Shares
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
                 'protocol':
                 {'in': 'query',
                  'description': 'Filter on protocol',
                  'type':'string',
                  'enum': PROTOCOLS,
                  'required': False}}
         )
    @marshal_with(NasSharesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List NAS shares
        """
        params = request.args
        protocol = params.get('protocol', None)
        if protocol != None:
            kwargs['proto'] = protocol.lower()
        response, code = list_shares(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(NasShareCreateSchema)
    @marshal_with(NasSharePaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create NAS shares
        """
        response, code = create_share(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'protocol':
                 {'in': 'query',
                  'description': 'Filter on protocol',
                  'type':'string',
                  'enum': PROTOCOLS,
                  'required': False}})
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete NAS shares
        """
        params = request.args
        protocol = params.get('protocol', None)
        if protocol != None:
            kwargs['proto'] = protocol.lower()
        response, code = delete_shares(kwargs)
        return (response, code)

@ddoc
class ShareResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: NAS Shares
    """
    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(NasSharePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get NAS share by name
        """
        response, code = get_share(kwargs['name'])
        return (response, code)

    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @use_kwargs(NasShareEditSchema)
    @marshal_with(NasSharePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit NAS share
        """
        response, code = update_share(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete NAS share by name
        """
        response, code = delete_share(kwargs['name'])
        return (response, code)

share_view_func  = ShareResource.as_view('share')
shares_view_func = SharesResource.as_view('shares')

nas_api.add_url_rule(
    'shares/<string:name>',
    view_func=share_view_func,
    methods=['GET', 'PATCH', 'DELETE'])

nas_api.add_url_rule(
    'shares/',
    view_func=shares_view_func,
    methods=['GET', 'POST', 'DELETE'])