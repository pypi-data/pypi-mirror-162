from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.nas_schemas import (NfsSharehostCreateSchema,
                                               NfsSharehostsPaginatedSchema,
                                               NfsSharehostPaginatedSchema)

from infiniguard_api.controller.nas.sharehost import (create_sharehost,
                                                  list_sharehosts,
                                                  get_sharehost,
                                                  delete_sharehosts,
                                                  delete_sharehost)

from flask import request

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class NfsShareHostsResource(MethodResource):
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
    @marshal_with(NfsSharehostsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List hosts for a specified NFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        response, code = list_sharehosts(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(NfsSharehostCreateSchema)
    @marshal_with(NfsSharehostPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Grant a host's access right to a NFS share
        """
        kwargs['data']['share'] = kwargs.pop('share_name')
        response, code = create_sharehost(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove all hosts' access rights to a NFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        response, code = delete_sharehosts(kwargs)
        return (response, code)

@ddoc
class NfsShareHostResource(MethodResource):
    """
    :Methods: GET, DELETE
    :Tags: NAS NFS Shares
    """
    @ddoc
    @doc(params={'share_host_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'share_host_name',
                  'required': True}
                 })
    @marshal_with(NfsSharehostPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get host names of a NFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        kwargs['host']  = kwargs.pop('share_host_name')
        response, code = get_sharehost(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'share_host_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'host1',
                  'name': 'share_host_name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove a host's access right to a NFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        kwargs['host']  = kwargs.pop('share_host_name')
        response, code  = delete_sharehost(kwargs)
        return (response, code)

nfs_shares_host_view_func  = NfsShareHostResource.as_view('nfs_sharehost')
nfs_shares_hosts_view_func = NfsShareHostsResource.as_view('nfs_sharehosts')

nas_api.add_url_rule(
    'nfs/shares/<string:share_name>/share_hosts',
    view_func=nfs_shares_hosts_view_func,
    methods=['GET', 'POST', 'DELETE'])

nas_api.add_url_rule(
    'nfs/shares/<string:share_name>/share_hosts/<string:share_host_name>',
    view_func=nfs_shares_host_view_func,
    methods=['GET','DELETE'])
