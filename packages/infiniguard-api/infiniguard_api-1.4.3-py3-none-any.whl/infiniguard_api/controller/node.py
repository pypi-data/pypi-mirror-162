import os
from threading import Thread
from time import sleep

from infiniguard_api.common.const import INFINIDAT_ROLE, ADMIN_ROLE, TECHNICIAN_ROLE
from infiniguard_api.lib.rest.common import http_code, allowed_roles, requires_approval

from infiniguard_api.common import messages
from infiniguard_api.lib.hw.cli_handler import run_syscli
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import error_handler, build_empty_response
from infiniguard_api.lib.hw.output_parser import check_command_successful


log = iguard_logging.get_logger(__name__)


@error_handler
@requires_approval('DDE App will reboot.')
@allowed_roles(roles=[INFINIDAT_ROLE, ADMIN_ROLE, TECHNICIAN_ROLE])
def reboot(**kwargs):
    wait_time = kwargs.pop('wait_time', 0)
    reboot_thread(wait_time)
    return build_empty_response(), http_code.OK


def reboot_system(wait):
    sleep(wait)
    log.warn(messages.REBOOTING_SYSTEM)
    command_line = ['/opt/DXi/syscli', '--nodemanage', '--reboot', '--sure']
    infiniguard_reboot = os.environ.get('INFINIGUARD_REBOOT', "1") == "1"
    if infiniguard_reboot:
        run_syscli(command_line, check_command_successful, 'system')


def reboot_thread(wait_time):
    thread = Thread(target=reboot_system, args=(wait_time,))
    log.warn(messages.REBOOTING_TIME_WARNING.format(wait_time))
    thread.start()
