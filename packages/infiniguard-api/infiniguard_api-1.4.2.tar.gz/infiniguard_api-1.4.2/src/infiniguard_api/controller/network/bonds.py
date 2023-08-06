"""
***Endpoint:***
 /network/bonds/

***Methods:***
 POST, GET, PATCH, DELETE

***CLI Commands:***
    syscli --edit netcfg --devname <DEVNAME> [--mtu <SIZE>] [--mode RR|AB|LACP] [--slaves <DEV1>,<DEV2>,<...>]
        [--nat <NAT_IPADDR>|none] [--extHostIp YES|NO] [--sure]
    syscli --edit netcfg --devname <DEVNAME> [--mtu <SIZE>] [--mode RR|AB|LACP] [--slaves <DEV1>,<DEV2>,<...>]
        [--nat <NAT_IPADDR>|none] [--extHostIp YES|NO] [--sure]
    syscli --del netcfg --devname <DEVNAME> [--sure]

"""

from infiniguard_api.lib.rest.common import http_code
from collections import OrderedDict
import re
from marshmallow import ValidationError
from infiniguard_api.controller.network.list_interface_xml import build_response
from infiniguard_api.model.validators import validate_devname
from infiniguard_api.common import messages
from infiniguard_api.controller.network.interfaces import (create_interface,
                                                           retrieve_interface,
                                                           update_interface,
                                                           delete_interface)
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import check_command_successful, parse_list_interface
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.iguard_api_exceptions import IguardApiWithCodeException
from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model, http_code)

log = iguard_logging.get_logger(__name__)


def filter_bonds(data):
    if not isinstance(data, list):
        return data
    bonds = [d for d in data if d['type'] == 'Bond']
    return bonds


def create_bond(request):
    """
    A bond device is created when an interface is created on it. In addition to the standard parameters for
    creating an interface, slave and mode information are also provided to create the bond device.

    **Command:**
        syscli --add netcfg --devname <DEVNAME> [--dhcp]|[--ipaddr <IPADDR> --netmask <NETMASK> --gateway <GATEWAY>]
            [--slaves <DEV1>,<DEV2>,<...>] [--mode RR|AB|LACP]
            [--mtu <SIZE>] [--defaultgw YES] [--segments REP,MGMT,DATA] [--nat <NAT_IPADDR>] [--hosts <IP1,IP2,IP3>]
            [--extHostIp YES] [--sure]

    :param request: model.network.BondCreateSchema

    :returns:
        response: model.network.BondPaginatedSchema
        code: HTTP Status Code

    :example:
            {
              "name": "bond0",
              "mtu": 1500,
              "options": "mode=0",
              "slaves": [ "p4p1", "p4p2"],
            }

    """
    response, code = create_interface(request)
    if code != http_code.ACCEPTED:
        return response, code

    response, qualifier, code = retrieve_bond(
        {'name': request.get('devname', '').split(':')[0]})
    if code != http_code.OK:
        return response, code

    response['message'] = messages.DDE_REBOOT_MSG
    return response, http_code.ACCEPTED


def xlate_options(d):
    match = re.search(r'.*mode=([0-9]).*', d['options'])
    if not match:
        raise Exception('Mode not specified: {}'.format(d['options']))
    d['mode'] = {0: 'RR', 1: 'AB', 4: 'LACP'}[int(match.group(1))]
    d.pop('options')
    return d


def convert_to_response(data):
    """Convert the result of the

    Args:
        data: gets a JSON array of dicts containing interface config in CLI format

    Returns:
        array of model.network.InterfaceSchema

    """
    try:
        translate_map = {"device_name": "devname", "type": "type", "slaves": "slave_names", "algorithm": "options",
                         "mtu": "mtu", "configured": "configured"}
        data = [{translate_map[k]: d[k] for k in translate_map.keys()} for d in data if d['type'] == 'Bond']
        data = [xlate_options(d) for d in data]
        return data
    except Exception as e:
        raise ValidationError(e)


def retrieve_bond(request):
    """
    Command:
        syscli --list interface --xml

    Args:
        request: None or {"name": "bond_name"}

    Returns:
        response: model.network.BondPaginatedSchema or model.network.BondsPaginatedSchema
        qualifier: "object" or "list"
        code: HTTP Status Code

    Examples:
        request: None
        response:
            [{
              "name": "bond0",
              "mtu": 1500,
              "options": "mode=0",
              "slaves": [ "p4p1", "p4p2"],
            },
            {
              "name": "bond1",
              "mtu": 1500,
              "options": "mode=0",
              "slaves": [ "p4p3", "p4p4"],
            }]

            {
              "name": "bond0",
              "mtu": 1500,
              "options": "mode=0",
              "slaves": [ "p4p3", "p4p4"],
            }

    """
    data, errmsg = run_syscli1('list', 'interface', parse_list_interface)
    if errmsg:
        error = dict(error=dict(message=[errmsg], code='BAD_REQUEST'))
        return error, None, http_code.BAD_REQUEST
    data = convert_to_response(data)

    if request.get('name', None):
        try:
            validate_devname(request['name'])
        except ValidationError as e:
            error = build_error_model(
                error_message=build_error_message(
                    {'retrieve_bond': e.messages}),
                error_code='BAD_REQUEST')
            return (build_entity_response(error=error), 'object', http_code.BAD_REQUEST)

        data = [d for d in data if d['devname'] == request['name']]
        data = data[0] if data else {}
        if not data:
            error = build_error_model(
                error_message=build_error_message(
                    {'retrieve_bond': 'Bond not found'}),
                error_code='BOND_NOT_FOUND')
            return (build_entity_response(error=error), 'object', http_code.NOT_FOUND)

    return build_response(request, data)


def update_bond(request):
    """
    A bond device can only be created by creating an interface on it. In addition to the standard parameters for
    creating an interface, slave and mode information are also provided to create the bond device.

    **Command:**
        syscli --edit netcfg --devname <DEVNAME> [--slaves <DEV1>,<DEV2>] [--mode RR|AB|LACP] [--sure]

    :param request: model.network.BondCreateSchema

    :returns:
        response: model.network.BondPaginatedSchema
        code: HTTP Status Code

    :example:
            {
              "name": "bond0",
              "mtu": 1500,
              "options": "mode=0",
              "slaves": [ "p4p1", "p4p2"],
            }

    """
    try:
        if request.get('errors', None):
            error = dict(error=dict(message=build_error_message(
                request['errors']), code='BAD_REQUEST'))
            log.error(error)
            return error, http_code.BAD_REQUEST

        bond_dict = request
        bond_dict['devname'] = request.pop('name', None)

        intf_args = ['sure']
        result, errmsg = run_syscli1(
            'edit', 'netcfg', check_command_successful, *intf_args, **bond_dict)
        if not result:
            if 'E8061301' in errmsg:
                code = http_code.NOT_FOUND
                error = build_error_model(
                    error_message=build_error_message(
                        {'update_bond': 'Interface not found'}),
                    error_code='BOND_NOT_FOUND')
            else:
                error = build_error_model(
                    error_message=build_error_message(
                        {'update_bond': errmsg}),
                    error_code='INTERNAL_SERVER_ERROR')
                code = http_code.INTERNAL_SERVER_ERROR
            return (build_entity_response(error=error), code)

        response, qualifier, code = retrieve_bond(
            {'name': bond_dict['devname']})
        if code != http_code.OK or not isinstance(response.get('result', None), dict):
            error = build_error_model(
                error_message=build_error_message(
                    {'update_bond': 'Interface not found'}),
                error_code='BOND_NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)

        response['message'] = messages.NO_REBOOT_REQUIRED
        return response, http_code.ACCEPTED
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, e.code
    except Exception as e:
        error = build_error_model(
            error_message=build_error_message(
                {'update_bond': getattr(e, 'message', str(e))}),
            error_code='INTERNAL_SERVER_ERROR')
        return (build_entity_response(error=error), http_code.INTERNAL_SERVER_ERROR)


def delete_bond(name=None):
    """First, delete the interface on the bond device. Then, specifically delete the bond device
    since deleting the interface does not delete the underlying bond device (this is unlike
    creation, where a bond device cannot be created without creating an interface on it.
    Command:
        syscli --del netcfg --devname <DEVNAME> [--sure]

    Args:
        name: Full device name of L3 bonded interface

    Returns:
        data: Message to reboot dde
        code: HTTP Status Code

    """
    try:
        validate_devname(name)
    except ValidationError as e:
        error = build_error_model(
                error_message=build_error_message(
                    {'delete_bond': e.messages}),
                error_code='BAD_REQUEST')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    response, qualifier, code = retrieve_bond({'name': name})
    if code != http_code.OK or not isinstance(response.get('result', None), dict):
        error = build_error_model(
            error_message=build_error_message(
                {'delete_bond': 'Bond not found'}),
            error_code='BOND_NOT_FOUND')
        return (build_entity_response(error=error), http_code.NOT_FOUND)
    return delete_interface(name)
