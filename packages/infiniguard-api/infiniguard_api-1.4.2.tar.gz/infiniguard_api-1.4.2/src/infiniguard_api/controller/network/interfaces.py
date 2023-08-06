"""
Endpoint: /network/interfaces/

Methods: POST, GET, PATCH, DELETE

CLI Commands:
    syscli --add netcfg --devname <DEVNAME> [--dhcp]|[--ipaddr <IPADDR> --netmask <NETMASK> --gateway <GATEWAY>]
        [--mtu <SIZE>] [--defaultgw YES] [--segments REP,MGMT,DATA] [--nat <NAT_IPADDR>] [--hosts <IP1,IP2,IP3>]
        [--extHostIp YES] [--slaves <DEV1>,<DEV2>,<...>] [--mode RR|AB|LACP] [--sure]
    syscli --edit netcfg --devname <DEVNAME> [--mtu <SIZE>] [--mode RR|AB|LACP] [--slaves <DEV1>,<DEV2>,<...>]
        [--nat <NAT_IPADDR>|none] [--extHostIp YES|NO] [--sure]
    syscli --del netcfg --devname <DEVNAME> [--sure]

"""
from collections import OrderedDict
import json
from marshmallow import ValidationError
from infiniguard_api.common import messages
from infiniguard_api.model.validators import validate_intfname
from infiniguard_api.controller.network.list_interface_xml import build_response
from infiniguard_api.controller.network import host
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import check_command_successful, parse_list_interface
from infiniguard_api.lib.iguard_api_exceptions import IguardApiWithCodeException
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model, http_code)

log = iguard_logging.get_logger(__name__)


def generate_intfname(devname_vlanid):
    parts = devname_vlanid.split(':')
    numparts = len(parts)
    # if full intfname specified then just return it
    if numparts == 2:
        return devname_vlanid

    response, qualifier, code = retrieve_interface({})

    if code != http_code.OK:
        error = dict(error=dict(message=[response], code='SYSTEM_ERROR'))
        raise IguardApiWithCodeException(
            error, http_code.INTERNAL_SERVER_ERROR)

    if not response:
        return '{}:1'.format(devname_vlanid)

    parts = devname_vlanid.split('.')
    devname = parts[0]
    result = response.get('result', [])
    interfaces = [int(d['intfname'].split(':')[1]) for d in result if d.get('devname', None) == devname and
                  d.get('intfname', None) is not None and ':' in d['intfname']]
    if not interfaces:
        return '{}:1'.format(devname_vlanid)
    interfaces.sort()

    max_intf = interfaces[-1] + 1
    for i in range(1, max_intf):
        if i not in interfaces:
            return '{}:{}'.format(devname_vlanid, i)
    return '{}:{}'.format(devname_vlanid, max_intf)


def filter_intf_by_intfname(name, data):
    """
    Filter an array of processed data from syscli by either the full interface name
    or by the devname if it is not an interface name (recognized by not having :1)
    Args:
        name: interface name of form devname[.vlanid]:interface_number or devname
        data: array of processed cli data

    Returns:
        array (1 or more) if input if devname or else a dictionary
    """
    parts = name.split(':')
    num_parts = len(parts)
    if num_parts > 2:
        raise ValidationError(
            "interfaces must be of the format: devname.vlanid:interface_number")
    # vlanid with no interface number
    if num_parts == 1 and len(parts[0].split('.')) > 1:
        raise ValidationError("vlanid provided with no interface number")
    check_field = 'intfname' if num_parts == 2 else 'devname'
    data = [d for d in data if d.get(check_field, None) == name]
    if check_field == 'intfname':
        if len(data) > 1:
            error = dict(error=dict(message=[
                         'only one interface with name: {} can exist'.format(name)], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(
                error, http_code.INTERNAL_SERVER_ERROR)
        return data[0] if data else {}
    return data


def create_interface(request):
    """
    Command:
        syscli --add netcfg --devname <DEVNAME> [--dhcp]|[--ipaddr <IPADDR> --netmask <NETMASK> --gateway <GATEWAY>]
            [--mtu <SIZE>] [--defaultgw YES] [--segments REP,MGMT,DATA] [--nat <NAT_IPADDR>] [--hosts <IP1,IP2,IP3>]
            [--extHostIp YES] [--slaves <DEV1>,<DEV2>,<...>] [--mode RR|AB|LACP] [--sure]

    Args:
        request: model.network.LogicalInterfaceSchema

    Returns:
        response: model.network.LogicalInterfacePaginatedSchema
        code: HTTP Status Code

    Examples:
        {
            "default_gateway": "10.10.8.7",
            "ip": "10.10.8.7",
            "mask": "255.255.255.0",
            "segments": ["DATA"],
            "host_ip": "NO",
            "parent_interface": "bond0"
        }

    """
    try:
        if request.get('errors', None):
            error = dict(error=dict(message=build_error_message(
                request['errors']), code='BAD_REQUEST'))
            raise IguardApiWithCodeException(error, http_code.BAD_REQUEST)

        intf_dict = request
        intf_dict['devname'] = generate_intfname(intf_dict.get('devname', None))

        if intf_dict.get('extHostIp', None):
            host.set_default_gateway(intf_dict)

        intf_args = ['sure']
        result, errmsg = run_syscli1(
            'add', 'netcfg', check_command_successful, *intf_args, **intf_dict)
        if not result:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(
                error, http_code.INTERNAL_SERVER_ERROR)

        # even though this is called devname it is intfname
        response, qualifier, code = retrieve_interface(
            {'name': intf_dict['devname']})
        if code != http_code.OK or not response or not isinstance(response.get('result', None), dict):
            error = build_error_model(
            error_message=build_error_message(
                {'create_interface': "No interface {} found after creating successfully".
                                             format(intf_dict['devname'])}),
            error_code='INTERFACE_NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)

        response['message'] = messages.DDE_REBOOT_MSG
        return response, http_code.ACCEPTED
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, e.code
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, http_code.INTERNAL_SERVER_ERROR


def convert_from_request(data):
    try:
        if data.get('intfname', None):
            data['devname'] = data.pop('intfname')
        if data.pop('ext_host_ip', False):
            data['extHostIp'] = 'YES'
        if data.get('ip_address', None):
            data['ipaddr'] = data.pop('ip_address')
        if data.get('segments', None):
            data['segments'] = data['segments'][0] if len(
                data['segments']) == 1 else ','.join(data['segments'])
            if data['segments'] == 'ALL':
                data.pop('segments')
        if data.get('hosts', None) and data['hosts']:
            data['hosts'] = ','.join(data['hosts'])
        return data
    except Exception as e:
        raise ValidationError(e)


def convert_to_response(data):
    """Convert the result of the

    Args:
        data: gets a JSON array of dicts containing interface config in CLI format

    Returns:
        array of model.network.InterfaceSchema

    """
    try:
        translate_map = {"device_name": "devname", "connection": "carrier", "state": "operstate",
                         "interface_name": "intfname", "exthostip": "ext_host_ip", "nat_ip_address": "nat"}
        rdata = []
        for d in data:
            stop = False
            if not d or not isinstance(d, OrderedDict):
                stop = True
            if d.get('type', None) == 'Port' and not d.get('device_name', '').startswith('p'):
                stop = True
            if d.get('type', None) == 'Bond':
                for s in d.get('slaves', []):
                    if not s.startswith('p'):
                        stop = True
                        break
            if stop:
                continue
            rd = {translate_map.get(k, k): v for k, v in d.items()}
            rd['ext_host_ip'] = rd.get('ext_host_ip', False) == 'YES'
            rd['configured'] = rd.get('configured', False) == 'true'
            rd.pop('default_gateway', None)
            rd['segments'] = [r['segment'] for r in rd.get('segments', [])]
            for r in rd.get('routes', []):
                if r['destination']:
                    r['network'] = r.pop('destination')
            rdata.append(rd)
        discard_keys = ['boot_protocol', 'maximum_speed']
        [r.pop(key, None) for key in discard_keys for r in rdata]
        return rdata
    except Exception as e:
        raise ValidationError(e)


def retrieve_interface(request):
    """
    Command:
        syscli --list interface --xml

    Args:
        request: None or dict with key 'name'

    Returns:
        response: model.network.LogicalInterfacePaginatedSchema or model.network.LogicalInterfacesPaginatedSchema
        qualifier: "object" or "list"
        code: HTTP Status Code

    Examples:
        request: None
        response:
            [{
                "intfname": "bond0.10:1",
                "ip_address": "10.10.8.7",
                "mask": "255.255.255.0",
                "gateway": "10.10.8.7",
                "default_gateway": "NO",
                "segments": ["DATA"],
                "ext_host_ip": "NO",
                "devname": "bond0"
            },
            {
                "intfname": "p1p1:1",
                "ip_address": "1.2.3.4",
                "mask": "255.255.255.0",
                "gateway": "1.2.3.4",
                "default_gateway": "NO",
                "segments": ["ALL"],
                "ext_host_ip": "NO",
                "devname": "p1p1"
            }]

            {
                "intfname": "p1p2.10:1",
                "ip_address": "10.11.12.13",
                "mask": "255.255.255.0",
                "gateway": "10.11.12.1",
                "default_gateway": "NO",
                "segments": ["ALL"],
                "default_gateway": "NO",
                "ext_host_ip": "NO",
                "devname": "p1p2"
            }

        request: {"name": "bond0.10:1"}
        response:
            {
                "intfname": "bond0.10:1",
                "ip_address": "10.10.8.7",
                "mask": "255.255.255.0",
                "gateway": "10.10.8.7",
                "default_gateway": "NO",
                "segments": ["DATA"],
                "ext_host_ip": "NO",
                "devname": "bond0"
            }

    """
    try:
        data, errmsg = run_syscli1('list', 'interface', parse_list_interface)
        if errmsg:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            return error, None, http_code.INTERNAL_SERVER_ERROR

        data = convert_to_response(data)
        if request.get('name', None):
            try:
                validate_intfname(request['name'], only_intf=True)
            except ValidationError as e:
                error = build_error_model(
                    error_message=build_error_message(
                        {'retrieve_interface': e.messages}),
                    error_code='BAD_REQUEST')
                return (build_entity_response(error=error), 'object', http_code.BAD_REQUEST)

            data = filter_intf_by_intfname(request['name'], data)
            if not data:
                error = build_error_model(
                    error_message=build_error_message(
                        {'retrieve_interface': 'Interface not found'}),
                    error_code='INTERFACE_NOT_FOUND')
                return (build_entity_response(error=error), 'object', http_code.NOT_FOUND)

        return build_response(request, data)
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, None, e.code
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, None, http_code.INTERNAL_SERVER_ERROR


def update_interface(request):
    """
    Command:
        syscli --edit netcfg --devname <DEVNAME> [--mtu <SIZE>] [--nat <NAT_IPADDR>] [--extHostIp YES] [--sure]

    Args:
        request: model.network.LogicalInterfaceSchema

    Returns:
        response: model.network.LogicalInterfacePaginatedSchema
        code: HTTP Status Code

    Examples:
        {
            "default_gateway": "10.10.8.7",
            "ip": "10.10.8.7",
            "mask": "255.255.255.0",
            "segments": ["DATA"],
            "host_ip": "NO",
            "parent_interface": "bond0"
        }

    """
    try:
        if request.get('errors', None):
            error = dict(error=dict(message=build_error_message(
                request['errors']), code='BAD_REQUEST'))
            log.error(error)
            return error, http_code.BAD_REQUEST

        intf_dict = request
        intf_dict['devname'] = request.pop('name')

        # if ipaddr, netmask, gateway, or segments are in the keys we have to delete and re-create interface
        fields = ['ipaddr', 'netmask', 'gateway', 'segments']
        if any(field in request for field in fields):
            return recreate_interface(request)

        if request.get('extHostIp', None):
            new_dict = update_current_info_with_req(request)
            new_dict.update(intf_dict)
            host.set_default_gateway(new_dict)

        intf_args = ['sure']
        result, errmsg = run_syscli1(
            'edit', 'netcfg', check_command_successful, *intf_args, **intf_dict)
        if not result:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            return error, http_code.INTERNAL_SERVER_ERROR

        response, qualifier, code = retrieve_interface(
            {'name': intf_dict['devname']})
        if code != http_code.OK or not response or not isinstance(response.get('result', None), dict):
            error = build_error_model(
                error_message=build_error_message(
                    {'update_interface': 'Interface not found'}),
                error_code='INTERFACE_NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)
            
        response['message'] = messages.NO_REBOOT_REQUIRED
        return response, http_code.ACCEPTED
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, e.code
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, http_code.INTERNAL_SERVER_ERROR


def update_current_info_with_req(request):
    response, qualifier, code = retrieve_interface(
        {'name': request.get('devname', None)})
    if code != http_code.OK or not response or not isinstance(response.get('result', None), dict):
        error = dict(error=dict(
            message=['Error retrieving interface configuration'], code='INTERFACE_NOT_FOUND'))
        raise IguardApiWithCodeException(
            error, http_code.NOT_FOUND)

    rkeys = ['intfname', 'ip_address', 'netmask',
             'gateway', 'segments', 'mtu', 'ext_host_ip']
    return convert_from_request({k: v for k, v in response['result'].items() if k in rkeys})


def recreate_interface(request):
    # retrieve the current interface configuration
    # update the current configuration with the changed parameters
    # delete the existing interface
    # recreate the interface with the updated parameters
    new_dict = update_current_info_with_req(request)
    new_dict.update(request)
    request = new_dict
    delete_interface(request.get('devname', None))
    return create_interface(request)


def delete_interface(name=None):
    """
    Command:
        syscli --del netcfg --devname <DEVNAME> [--sure]

    Args:
        name: Full device name of L3 interface

    Returns:
        data: model.base_schema.MessageSchema
        code: HTTP Status Code
    """
    try:
        netcfg_args = ['sure']
        netcfg_kwargs = {'devname': name}
        result, errmsg = run_syscli1(
            'del', 'netcfg', check_command_successful, *netcfg_args, **netcfg_kwargs)
        if not result:
            error = dict(message=[errmsg], code='SYSTEM_ERROR')
            return dict(error=error), http_code.INTERNAL_SERVER_ERROR

        message = '{} deleted. '.format(name) + messages.DDE_REBOOT_MSG
        data = dict(message=message)
        return data, http_code.ACCEPTED
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, http_code.INTERNAL_SERVER_ERROR


def verify_same_gateway(intf_dict):
    """
    If extHostIp is YES or is also being updated, check that the new ip address and/or default gateway
    belong to same subnet as the host default gateway. If not, return False else return True.

    Args:
        intf_dict: request info

    Returns:
        True or False
    """
    try:
        if not intf_dict.get('host_ext_ip', False):
            return True

        response, qualifier, code = retrieve_interface(
            {'name': intf_dict['devname']})
        if code != http_code.OK or not response or not isinstance(response.get('result', None), dict):
            error = dict(error=dict(
                message=['Error retrieving interface'], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(
                error, http_code.INTERNAL_SERVER_ERROR)

        intf = response['result']
        if not intf.get('ext_host_ip', False):
            return True

        response, qualifier, code = host.retrieve_host({})
        if code != http_code.OK or not response or not response.get('result', None):
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(
                error, http_code.INTERNAL_SERVER_ERROR)

        network = response['result']
        default_gateway = network.get('default_gateway', None)
        if not default_gateway:
            return True

        return True
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, e.code
    except Exception as e:
        log.error(e.message)
        return False
