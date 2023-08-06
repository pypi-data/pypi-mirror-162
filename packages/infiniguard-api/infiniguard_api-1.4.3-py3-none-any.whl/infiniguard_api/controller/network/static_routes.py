"""
Endpoint:
    /network/static_routes/

Methods:
 POST, GET, DELETE

CLI Commands:
    syscli --add route [--devname <DEVNAME>] --network <IPADDR> --netmask <NETMASK> --gateway <GATEWAY> [--sure]
    syscli --del route [--devname <DEVNAME>] --network <IPADDR> [--sure]
    syscli --list route [--devname <DEVNAME>]
"""

import six
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.common import messages
from infiniguard_api.controller.network.list_interface_xml import build_response, get_object_count
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import check_command_successful, parse_config_style
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import build_error_message
from infiniguard_api.lib.iguard_api_exceptions import IguardApiWithCodeException
from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model, http_code)
log = iguard_logging.get_logger(__name__)


def filter_by_ipaddr(routes, network):
    r = [r for r in routes if r['network'] == network]
    return r[0] if len(r) == 1 else {}


def create_static_route(request):
    """
    CLI Commands:
        syscli --add route [--devname <DEVNAME>] --network <IPADDR> --netmask <NETMASK> --gateway <GATEWAY> [--sure]

    Args:
        request: model.network.StaticRouteSchema

     Returns:

            model.network.StaticRoutePaginatedSchema
            code: HTTP Status Code

    """
    try:
        if request.get('errors', None):
            error = dict(error=dict(message=build_error_message(
                request['errors']), code='BAD_REQUEST'))
            log.error(error)
            return error, http_code.BAD_REQUEST

        args = ['sure']
        add_parms = request
        result, errmsg = run_syscli1(
            'add', 'route', check_command_successful, *args, **add_parms)
        if errmsg or not result:
            error = build_error_model(
                error_message=build_error_message(
                    {'create_static_route': errmsg}),
                error_code='INTERNAL_SERVER_ERROR')
            return (build_entity_response(error=error), http_code.INTERNAL_SERVER_ERROR)

        list_parms = {'devname': add_parms['devname']} if add_parms.get(
            'devname', None) else {}
        data, errmsg = run_syscli1(
            'list', 'route', parse_config_style, **list_parms)
        if errmsg or not data:
            error = build_error_model(
                error_message=build_error_message(
                    {'create_static_route': errmsg}),
                error_code='INTERNAL_SERVER_ERROR')
            return (build_entity_response(error=error), http_code.INTERNAL_SERVER_ERROR)

        route = dict(
            network=add_parms['network'], netmask=add_parms['netmask'], gateway=add_parms['gateway'])
        routes = [r for r in data if r == route]

        if not routes:
            error = build_error_model(
                error_message=build_error_message(
                    {'create_static_route': 'Couldn\'t get route after creating it'}),
                error_code='INTERNAL_SERVER_ERROR')
            return (build_entity_response(error=error), http_code.INTERNAL_SERVER_ERROR)

        request['name'] = add_parms['network']
        response, qualifier, code = build_response(request, routes[0])
        response['message'] = messages.DDE_REBOOT_MSG
        if code != http_code.OK:
            return response, code

        return response, http_code.ACCEPTED
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, http_code.INTERNAL_SERVER_ERROR


def retrieve_static_routes(request):
    """
    CLI Commands:
            syscli --list route [--network <IPNETADDR>]

    Args:
        request: either no argument or network address

    Returns:
        data: model.network.StaticRoutesPaginatedSchema or model.network.StaticRoutePaginatedSchema
        qualifier: either "object" or "list"
        code: HTTP Status Code

    Examples:
        [{"network": "10.10.10.0","mask": "255.255.255.0", "gateway": "0.0.0.0"},...]

    """
    try:
        kwargs = {'devname': request['devname']
                  } if request.get('devname', None) else {}
        data, errmsg = run_syscli1(
            'list', 'route', parse_config_style, **kwargs)
        if errmsg:
            error = build_error_model(
                error_message=build_error_message(
                    {'retrieve_static_routes': [errmsg]}),
                error_code='SYSTEM_ERROR')
            return (build_entity_response(error=error), None, http_code.INTERNAL_SERVER_ERROR)

        if request.get('network', None):
            request['name'] = request['network']
            data = filter_by_ipaddr(data, request['network'])

        if not data and (request.get('network', None) or request.get('devname', None)):
            error = build_error_model(
                error_message=build_error_message(
                    {'retrieve_static_routes': 'Route not found'}),
                error_code='ROUTE_NOT_FOUND')
            return (build_entity_response(error=error), None, http_code.NOT_FOUND)
        return build_response(request, data)
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, None, e.code
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, None, http_code.INTERNAL_SERVER_ERROR


def delete_static_route(kwargs):
    """
    CLI Commands:
            syscli --del route [--devname <DEVNAME>] --network <IPADDR> [--sure]

    Args:
        network address of device to delete

    Returns:
        data: model.base_schema.MessageSchema
        code: HTTP Status Code

    """
    try:
        args = ['sure']
        result, errmsg = run_syscli1(
            'del', 'route', check_command_successful, *args, **kwargs)
        if errmsg or not result:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(
                error=error, code=http_code.INTERNAL_SERVER_ERROR)
        devname = kwargs.get('devname', None)
        network = kwargs['network']
        message = 'Static route: {} deleted{}'.format(network,
                                                      ' on {}. '.format(devname) if devname else '. ') + messages.DDE_REBOOT_MSG
        data = dict(message=message)
        return data, http_code.ACCEPTED
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, e.code
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, http_code.INTERNAL_SERVER_ERROR
