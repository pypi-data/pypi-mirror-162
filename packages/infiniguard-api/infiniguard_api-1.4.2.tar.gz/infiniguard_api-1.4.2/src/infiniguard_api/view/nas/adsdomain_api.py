from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, JoinMessageSchema, DisjoinMessageSchema

from infiniguard_api.model.nas_schemas import (CifsAdsDomainCreateSchema)

from infiniguard_api.controller.nas.adsdomain import (join_adsdomain,
                                                      disjoin_adsdomain)

from flask import request

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class CifsAdsDomainsResource(MethodResource):
    """
    :Methods: POST
    :Tags: NAS CIFS ADS Domains
    """
    @ddoc
    @use_kwargs(CifsAdsDomainCreateSchema)
    @marshal_with(JoinMessageSchema(exclude=("metadata",)), http_code.OK, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Join the Samba server to an ADS domain
        """
        response, code = join_adsdomain(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'admin':
                 {'in': 'query',
                  'description': 'User name of any account that has the right to disjoin the ADS domain',
                  'type': 'string',
                  'required': False}})
    @doc(params={'password':
                 {'in': 'query',
                  'type': 'string',
                  'name': 'password',
                  'required': False}})
    @marshal_with(DisjoinMessageSchema(exclude=("metadata",)), code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Disjoin the Samba server from an ADS domain
        """
        params = request.args
        admin =  params.get('admin', None)
        if admin:
            kwargs['admin'] = admin
        password = params.get('password', None)
        if password:
            kwargs['password'] = password
        response, code = disjoin_adsdomain(kwargs)
        return (response, code)

cifs_ads_domains_view_func = CifsAdsDomainsResource.as_view('cifs_adsdomains')

nas_api.add_url_rule(
    'cifs/ads_domains',
    view_func=cifs_ads_domains_view_func,
    methods=['POST', 'DELETE'])

