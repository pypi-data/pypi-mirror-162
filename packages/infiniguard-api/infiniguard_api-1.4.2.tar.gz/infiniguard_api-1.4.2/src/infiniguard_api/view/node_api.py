from flask_apispec import use_kwargs, marshal_with, doc, MethodResource
from flask import Blueprint
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.model.base_schema import EmptyResponseSchema, ErrorResponseSchema
from infiniguard_api.model.node_schemas import NodeRebootSchema
from infiniguard_api.controller.node import reboot
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

node_api = Blueprint('node_api', __name__)
log = iguard_logging.get_logger(__name__)


@ddoc
class RebootResource(MethodResource):
    """
    :Methods: POST
    :Tags: DDE Nodes
    """
    @ddoc
    @use_kwargs(NodeRebootSchema)
    @marshal_with(EmptyResponseSchema, http_code.OK, description="EmptyResponseSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Reboot the system
        :Description: Reboot the system with an optional wait time of 1s to 10m.
        """
        response, code = reboot(**kwargs)
        return response, code


reboot_view_func = RebootResource.as_view('reboot')

node_api.add_url_rule(
    'reboot',
    view_func=reboot_view_func,
    methods=['POST'])
