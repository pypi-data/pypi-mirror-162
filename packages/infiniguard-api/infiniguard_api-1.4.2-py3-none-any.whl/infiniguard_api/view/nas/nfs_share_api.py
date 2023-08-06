from flask_apispec import (use_kwargs, marshal_with,
                           doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.nas_schemas import (NasShareCreateSchema,
                                               NasShareEditSchema,
                                               NfsSharesPaginatedSchema,
                                               NfsSharePaginatedSchema)

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


@ddoc
class NfsSharesResource(MethodResource):
    """
    :Methods: GET, POST, DELETE
    :Tags: NAS NFS Shares
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
    @marshal_with(NfsSharesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List NFS shares
        """
        kwargs['proto'] = 'nfs'
        response, code = list_shares(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(NasShareCreateSchema(exclude=['protocol']))
    @marshal_with(NfsSharePaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create NFS share
        """
        kwargs['proto'] = 'nfs'
        response, code = create_share(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete all NFS shares
        """
        cli_dict = {'proto': 'nfs'}
        response, code = delete_shares(cli_dict)
        return (response, code)


@ddoc
class NfsShareResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: NAS NFS Shares
    """
    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(NfsSharePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get NFS share by name
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
    @marshal_with(NfsSharePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit NFS shares
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
        :Summary: Delete NFS share by name
        """
        response, code = delete_share(kwargs['name'])
        return (response, code)


nfs_share_view_func = NfsShareResource.as_view('nfs_share')
nfs_shares_view_func = NfsSharesResource.as_view('nfs_shares')

nas_api.add_url_rule(
    'nfs/shares/<string:name>',
    view_func=nfs_share_view_func,
    methods=['GET', 'PATCH', 'DELETE'])

nas_api.add_url_rule(
    'nfs/shares/',
    view_func=nfs_shares_view_func,
    methods=['GET', 'POST', 'DELETE'])
