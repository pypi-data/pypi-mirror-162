from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema

from infiniguard_api.model.nas_schemas import (NfssettingPaginatedSchema)

from infiniguard_api.controller.nas.nfssetting import (get_nfssetting,
                                                       set_nfssetting)

from flask import request
from marshmallow.fields import Str
from marshmallow import validate

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class NfsNfssettingResource(MethodResource):
    """
    :Methods: GET, PATCH
    :Tags: NAS NFS Settings
    """
    @ddoc
    @marshal_with(NfssettingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get NFS settings
        """
        response, code = get_nfssetting(kwargs)
        return (response, code)

    @ddoc
    @use_kwargs({'secure': Str(validate=validate.OneOf(['yes', 'no']), required=True, example='yes')})
    @marshal_with(NfssettingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Set NFS settings
        """
        response, code = set_nfssetting(kwargs)
        return (response, code)

nfs_nfssetting_view_func = NfsNfssettingResource.as_view('nfs_nfssetting')

nas_api.add_url_rule(
    'nfs/nfssetting',
    view_func=nfs_nfssetting_view_func,
    methods=['GET', 'PATCH'])