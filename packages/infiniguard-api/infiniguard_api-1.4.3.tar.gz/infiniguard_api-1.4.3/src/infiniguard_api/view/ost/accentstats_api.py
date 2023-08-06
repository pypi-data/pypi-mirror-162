from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.ost_schemas import (OstaccentstatsSchema)

from infiniguard_api.controller.ost.accentstats import (get_accentstats)

from infiniguard_api.view.ost import ost_api

@doc(tags=['OST NetBoost Statistics'])
class OstaccentstatsResource(MethodResource):
    """
    Methods: GET
    """
    #@marshal_with(OstaccentstatsSchema)
    def get(self, **kwargs):
        """
        Get Ostsetting
        """
        response, code = get_accentstats(kwargs)
        return (response, code)

ost_accentstats_view_func = OstaccentstatsResource.as_view('accentstats')

ost_api.add_url_rule(
    'netbooststats',
    view_func=ost_accentstats_view_func,
    methods=['GET'])

