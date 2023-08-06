from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.controller.network.misc import backup_or_restore
from flask_apispec import MethodResource, doc, marshal_with
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema
from infiniguard_api.view.network.common import network_api
from infiniguard_api.lib.documentation import ddoc


@ddoc
class NetworkBackupResource(MethodResource):
    """
    :Methods: POST
    :Tags: Network Miscellaneous
    """

    @ddoc
    @marshal_with(MessageSchema, http_code.OK, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        """
        :Summary: Backup the network configuration
        """
        return backup_or_restore('backup')


@ddoc
class NetworkRestoreResource(MethodResource):
    """
    :Methods: POST
    :Tags: Network Miscellaneous
    """

    @ddoc
    @marshal_with(MessageSchema, http_code.OK, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self):
        """
        :Summary: Restore the network configuration
        """
        return backup_or_restore('restore')


netcfg_backup_view_func = NetworkBackupResource.as_view('backup')

network_api.add_url_rule('backup/', view_func=netcfg_backup_view_func, methods=['POST'])

netcfg_restore_view_func = NetworkRestoreResource.as_view('restore')

network_api.add_url_rule('restore/', view_func=netcfg_restore_view_func, methods=['POST'])
