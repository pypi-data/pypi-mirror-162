from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)
from flask import request

from infiniguard_api.model.ost_schemas import (OstTlscertificateCreateSchema,
                                               OstTlscertificatesPaginatedSchema)

from infiniguard_api.controller.ost.tlscertificate import (install_tlscertificate,
                                                           restore_tlscertificate,
                                                           list_tlscertificates)

from infiniguard_api.view.ost import ost_api

@doc(tags=['OST TLS Certificates'])
class TlscertificateResource(MethodResource):
    """
    Methods: GET, POST
    """
    @marshal_with(OstTlscertificatesPaginatedSchema)
    def get(self, **kwargs):
        """
        List TLS certificates
        """
        response, code = list_tlscertificates(kwargs)
        return (response, code)

    @use_kwargs(OstTlscertificateCreateSchema)
    def post(self, **kwargs):
        path = request.path
        operation = path.split('/')[-1]
        if operation == 'install':
            response, code = install_tlscertificate(kwargs)
        else:
            response, code = restore_tlscertificate()
        return (response, code)

ost_tlscertificate_view_func = TlscertificateResource.as_view('tlscertificate')

ost_api.add_url_rule(
    'tlscertificates',
    view_func=ost_tlscertificate_view_func,
    methods=['GET'])

ost_api.add_url_rule(
    'tlscertificates/install',
    view_func=ost_tlscertificate_view_func,
    methods=['POST'])

ost_api.add_url_rule(
    'tlscertificates/restore',
    view_func=ost_tlscertificate_view_func,
    methods=['POST'])