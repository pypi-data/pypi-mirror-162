from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, JoinMessageSchema, DisjoinMessageSchema

from infiniguard_api.controller.nas.workgroup import (join_workgroup,
                                                      disjoin_workgroup)

from flask import request
from marshmallow.fields import Str
from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class CifsWorkgroupsResource(MethodResource):
    """
    :Methods: POST
    :Tags: NAS CIFS Workgroups
    """
    @ddoc
    @use_kwargs({'name': Str(required=True, example='workgroup1')})
    @marshal_with(JoinMessageSchema(exclude=("metadata",)), http_code.OK, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Join the Samba server to the specified workgroup
        """
        response, code = join_workgroup(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DisjoinMessageSchema(exclude=("metadata",)), code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Disjoin the Samba server from its workgroup
        """
        response, code = disjoin_workgroup(kwargs)
        return (response, code)

cifs_workgroups_view_func = CifsWorkgroupsResource.as_view('cifs_workgroups')

nas_api.add_url_rule(
    'cifs/workgroups',
    view_func=cifs_workgroups_view_func,
    methods=['POST', 'DELETE'])
