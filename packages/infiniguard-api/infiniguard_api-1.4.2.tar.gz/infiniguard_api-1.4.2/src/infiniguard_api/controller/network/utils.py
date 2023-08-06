import os
from threading import Thread
from time import sleep
from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import const, messages
from infiniguard_api.lib.hw.cli_handler import run_syscli, run_python, execute_command
from infiniguard_api.lib.hw.mtu import calculate_mtu
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import build_error_message, build_error_model, build_entity_response, error_handler, build_async_task_response
from infiniguard_api.lib.hw.output_parser import check_command_successful, parse_config_style, parse_async


log = iguard_logging.get_logger(__name__)


@error_handler
def ping(**cli_dict):
    cli_dict = cli_dict.get('data')
    src = cli_dict.get('src')
    dst = cli_dict.get('dst')
    timeout = cli_dict.get('time', 5)
    command_line = ['/bin/ping', '-w', '{}'.format(timeout), dst]
    if src:
        command_line += ['-I', src]
    result = run_syscli(command_line, parse_async, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run ping'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def ifconfig(**cli_dict):
    cli_dict = cli_dict.get('data')
    ifname = cli_dict.get('interface')
    command_line = ['/sbin/ifconfig']
    if ifname:
        command_line += [ifname]
    result = run_syscli(command_line, parse_async, 'system')

    if not result:
        error = build_error_model(
            error_message=['Failed to run ifconfig'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def mtu(**cli_dict):
    cli_dict = cli_dict.get('data')
    dst = cli_dict.get('dst')
    command_line = [dst]
    result = run_python(command_line, calculate_mtu, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run mtu'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def nslookup(**cli_dict):
    cli_dict = cli_dict.get('data')
    ip = cli_dict.get('dst')
    command_line = ['/usr/bin/nslookup', ip]
    result = run_syscli(command_line, parse_async, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run nslookup'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


def show_resolv(*args):
    try:
        with open('/etc/resolv.conf') as f:
            return 0, f.read(), ""
    except Exception as e:
        return 1, "", repr(e)


@error_handler
def resolv(**cli_dict):
    command_line = []
    result = run_python(command_line, show_resolv, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run resolv'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def traceroute(**cli_dict):
    cli_dict = cli_dict.get('data')
    src = cli_dict.get('src')
    dst = cli_dict.get('dst')
    device = cli_dict.get('interface')
    command_line = ['/bin/traceroute', dst]
    if src:
        command_line += ['-s', src]
    if device:
        command_line += ['-i', device]
    result = run_syscli(command_line, parse_async, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run traceroute'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def iperf(**cli_dict):
    cli_dict = cli_dict.get('data')
    version = cli_dict.get('iperf_version', 1)
    dst = cli_dict.get('dst')
    src = cli_dict.get('src')
    parallel = cli_dict.get('parallel')
    time = cli_dict.get('time')
    buffer_len = cli_dict.get('buffer_len')
    reverse = cli_dict.get('reverse')

    if int(version) == 3:
        command_line = ['/usr/bin/iperf3', '-c', dst]
    else:
        command_line = ['/usr/bin/iperf', '-c', dst]
    if src:
        command_line += ['-B', src]
    if parallel:
        command_line += ['-P', str(parallel)]
    if time:
        command_line += ['-t', str(time)]
    if buffer_len:
        command_line += ['-l', '{}K'.format(buffer_len)]
    if reverse:
        command_line += ['--reverse']
    result = run_syscli(command_line, parse_async, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run iperf'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


def get_bonds(*args):
    try:
        bond_id = None
        if args[0] is not []:
            bond_id = args[0][0]
        DIR = '/proc/net/bonding'
        if os.path.isdir(DIR):
            out = ''
            for bond in sorted(os.listdir(DIR)):
                if bond_id == None or bond == 'bond{}'.format(bond_id):
                    out += '{}:\n'.format(bond)
                    with open('{}/{}'.format(DIR, bond)) as f:
                        out += f.read()
                        out += '\n'
            if not out:
                raise Exception('Bond not found')
            return 0, out, ""
        else:
            raise Exception('No bonds found')
    except Exception as e:
        return 1, "", str(e)


@error_handler
def bonds(**cli_dict):
    cli_dict = cli_dict.get('data')
    bond_id = cli_dict.get('bond_id')
    command_line = [bond_id]
    result = run_python(command_line, get_bonds, 'system')
    if not result:
        error = build_error_model(
            error_message=['Failed to run bonds'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


def get_ethtool(*args):
    try:
        ifname = None
        if args[0] is not []:
            ifname = args[0][0]
        DIR = '/sys/class/net/'
        interfaces = sorted([a for a in os.listdir(DIR) if os.path.islink(
            DIR + '/' + a) and a != 'lo' and '.' not in a])

        res_out = ''
        res_rc = 0
        res_err = ''
        for interface in interfaces:
            if not ifname or interface == ifname:
                rc, out, err = execute_command(
                    ['/usr/sbin/ethtool', interface])
                res_rc += rc
                res_err += err
                res_out += out

        if not res_out and not res_err:
            raise Exception('Interface not found')

        return res_rc, res_out, res_err

    except Exception as e:
        return 1, "", str(e)


@error_handler
def ethtool(**cli_dict):
    cli_dict = cli_dict.get('data')
    ifname = cli_dict.get('interface')
    command_line = [ifname]
    result = run_python(command_line, get_ethtool, 'system')

    if not result:
        error = build_error_model(
            error_message=['Failed to run ethtool'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED
