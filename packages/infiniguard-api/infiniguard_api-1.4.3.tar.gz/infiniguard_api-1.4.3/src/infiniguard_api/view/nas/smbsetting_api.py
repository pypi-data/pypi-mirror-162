from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema

from infiniguard_api.model.nas_schemas import (SmbsettingEditSchema, SmbsettingPaginatedSchema)

from infiniguard_api.controller.nas.smbsetting import (get_smbsetting,
                                                       set_smbsetting,
                                                       SMBSETTING_OPTIONS)

from flask import request
from marshmallow.fields import Str
from marshmallow import validate

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class CifsSmbsettingResource(MethodResource):
    """
    :Methods: GET, PATCH
    :Tags: NAS CIFS SMB Settings
    """
    @ddoc
    @doc(params={'option':
                 {'in': 'query',
                  'description': "smbsetting options",
                  'type': 'string',
                  'enum': SMBSETTING_OPTIONS,
                  'required': True}})
    @marshal_with(SmbsettingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get CIFS SMB setting
        """
        params = request.args
        option = params.get('option', None)
        response, code = get_smbsetting(kwargs, option)
        return (response, code)

    @ddoc
    @use_kwargs(SmbsettingEditSchema)
    @marshal_with(SmbsettingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Set CIFS SMB setting
        """
        response, code = set_smbsetting(kwargs)
        return (response, code)

cifs_smbsetting_view_func = CifsSmbsettingResource.as_view('cifs_smbsetting')

nas_api.add_url_rule(
    'cifs/smbsetting',
    view_func=cifs_smbsetting_view_func,
    methods=['GET', 'PATCH'])