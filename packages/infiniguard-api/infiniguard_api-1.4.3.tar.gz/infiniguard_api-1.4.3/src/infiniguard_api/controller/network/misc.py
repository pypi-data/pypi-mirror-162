# pragma: no cover
from infiniguard_api.lib.rest.common import http_code
import six

from infiniguard_api.common import messages
from infiniguard_api.lib.iguard_api_exceptions import IguardApiWithCodeException
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import check_command_successful
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import build_error_message

log = iguard_logging.get_logger(__name__)


def backup_or_restore(cmd):
    try:
        if cmd not in ['backup', 'restore']:
            error = dict(error=dict(message='Bad cmd: {}'.format(request['cmd']), code='BAD_REQUEST'))
            raise IguardApiWithCodeException(error, http_code.BAD_REQUEST)

        result, errmsg = run_syscli1(cmd, 'netcfg', check_command_successful)
        if not result:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(error, http_code.INTERNAL_SERVER_ERROR)

        message = messages.NETCFG_BACKUP if cmd == 'backup' else messages.NETCFG_RESTORE
        return dict(message=message), http_code.OK
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, e.code
    except Exception as e:
            error = dict(error=dict(message=getattr(e, 'message', str(e)), code='UNEXPECTED_EXCEPTION'))
            log.error(error)
            return error, http_code.INTERNAL_SERVER_ERROR
