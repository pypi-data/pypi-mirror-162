from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema

from infiniguard_api.model.ost_schemas import (OstsettingPaginatedSchema,
                                               OstsettingEditSchema)

from infiniguard_api.controller.ost.ostsetting import (update_ostsetting,
                                                   get_ostsetting)

from infiniguard_api.view.ost import ost_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class OstsettingResource(MethodResource):
    """
    :Methods: GET, PATCH
    :Tags: OST Settings
    """
    @ddoc
    @marshal_with(OstsettingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get OST Setting
        """
        response, code = get_ostsetting(kwargs)
        return (response, code)

    @ddoc
    @use_kwargs(OstsettingEditSchema)
    @marshal_with(OstsettingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit OST setting
        """
        response, code = update_ostsetting(kwargs)
        return (response, code)

ost_ostsetting_view_func = OstsettingResource.as_view('ostsetting')

ost_api.add_url_rule(
    'ostsettings',
    view_func=ost_ostsetting_view_func,
    methods=['PATCH', 'GET'])

