from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.nas_schemas import (CifsShareadminsPaginatedSchema,
                                               CifsShareadminPaginatedSchema)

from infiniguard_api.controller.nas.shareadmin import (create_shareadmin,
                                                      list_shareadmins,
                                                      get_shareadmin,
                                                      delete_shareadmins,
                                                      delete_shareadmin)

from flask import request
from marshmallow.fields import Str

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class CifsShareAdminsResource(MethodResource):
    """
    :Methods: GET, POST, DELETE
    :Tags: NAS CIFS Shareadmins
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
    @marshal_with(CifsShareadminsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List share admin users
        """
        response, code = list_shareadmins(kwargs)
        return (response, code)

    @ddoc
    @use_kwargs({'name': Str(required=True, example='shareadmin1')})
    @marshal_with(CifsShareadminPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Add a share admin user
        """
        response, code = create_shareadmin(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Remove all share admin users
        """
        response, code = delete_shareadmins(kwargs)
        return (response, code)

@ddoc
class CifsShareAdminResource(MethodResource):
    """
    :Methods: DELETE
    :Tags: NAS CIFS Shareadmins
    """
    @ddoc
    @doc(params={'shareadmin_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'user1',
                  'name': 'shareadmin_name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete a share admin user
        """
        kwargs['name']  = kwargs.pop('shareadmin_name')
        response, code  = delete_shareadmin(kwargs)
        return (response, code)

cifs_shareadmin_view_func  = CifsShareAdminResource.as_view('cifs_shareadmin')
cifs_shareadmins_view_func = CifsShareAdminsResource.as_view('cifs_shareadmins')

nas_api.add_url_rule(
    'cifs/share_admins',
    view_func=cifs_shareadmins_view_func,
    methods=['GET', 'POST', 'DELETE'])

nas_api.add_url_rule(
    'cifs/share_admins/<string:shareadmin_name>',
    view_func=cifs_shareadmin_view_func,
    methods=['DELETE'])
