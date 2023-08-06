from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.nas_schemas import (CifsShareuserCreateSchema,
                                               CifsShareusersPaginatedSchema,
                                               CifsShareuserPaginatedSchema)

from infiniguard_api.controller.nas.shareuser import (create_shareuser,
                                                      list_shareusers,
                                                      get_shareuser,
                                                      delete_shareusers,
                                                      delete_shareuser)

from flask import request

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class CifsShareUsersResource(MethodResource):
    """
    :Methods: GET, POST, DELETE
    :Tags: NAS CIFS Shares
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
    @marshal_with(CifsShareusersPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List of workgroup users for a CIFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        response, code = list_shareusers(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(CifsShareuserCreateSchema(exclude=("share",)))
    @marshal_with(CifsShareuserPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Grant a workgroup user's access right to a CIFS share
        """
        kwargs['data']['share'] = kwargs.pop('share_name')
        response, code = create_shareuser(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove all workgroup users's access right from a CIFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        response, code = delete_shareusers(kwargs)
        return (response, code)

@ddoc
class CifsShareUserResource(MethodResource):
    """
    :Methods: GET, DELETE
    :Tags: NAS CIFS Shares
    """
    @ddoc
    @doc(params={'share_user_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'share_user_name',
                  'required': True}
                 })
    @marshal_with(CifsShareuserPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get workgroup user of a CIFS share by name
        """
        kwargs['share'] = kwargs.pop('share_name')
        kwargs['user']  = kwargs.pop('share_user_name')
        response, code = get_shareuser(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'share_user_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'user1',
                  'name': 'share_user_name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove a workgroup user's access right to a CIFS share
        """
        kwargs['share'] = kwargs.pop('share_name')
        kwargs['user']  = kwargs.pop('share_user_name')
        response, code  = delete_shareuser(kwargs)
        return (response, code)

cifs_shares_user_view_func  = CifsShareUserResource.as_view('cifs_shareuser')
cifs_shares_users_view_func = CifsShareUsersResource.as_view('cifs_shareusers')

nas_api.add_url_rule(
    'cifs/shares/<string:share_name>/share_users',
    view_func=cifs_shares_users_view_func,
    methods=['GET', 'POST', 'DELETE'])

nas_api.add_url_rule(
    'cifs/shares/<string:share_name>/share_users/<string:share_user_name>',
    view_func=cifs_shares_user_view_func,
    methods=['GET','DELETE'])
