"""
Endpoints:
    /network/host/

Methods:
    POST, GET, PATCH

CLI Commands:
    syscli --set network [--hostname <HOSTNAME>] [--domain <DOMAINNAME>] [--dns <IPADDR,...>]
        [--defaultgateway <DEFAULTGATEWAY>] [--sure]
    syscli --get network
"""

from marshmallow import ValidationError
from infiniguard_api.common import messages
from infiniguard_api.controller.network.list_interface_xml import build_response
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import check_command_successful, parse_config_style_raw
from infiniguard_api.lib.iguard_api_exceptions import IguardApiWithCodeException
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import build_error_message
from infiniguard_api.lib.rest.common import http_code

log = iguard_logging.get_logger(__name__)


def create_or_update_host(request, update=False):
    """
    Description:
    The same command is used to create or update. Any field can be changed.
    Passing a field with no argument will delete the value.


    Command:
     syscli --set network [--hostname <HOSTNAME>] [--domain <DOMAINNAME>] [--dns <IPADDR,...>]
        [--defaultgateway <DEFAULTGATEWAY>] [--sure]

    Args:
        request: model.network.HostSchema
        update: False for POST, True for PATCH

    Returns:
        response: model.network.HostPaginatedSchema
        code: HTTP Status Code

    Examples:
        {
            "DNS_Cache": "Disabled",
            "DNS_Servers": [{"DNS_Server": "172.16.0.10"}],
            "Domain": "localdomain",
            "Name": "dde1-2271"
        }

    """
    try:
        if request.get('errors', None):
            error = dict(error=dict(message=build_error_message(
                request['errors']), code='BAD_REQUEST'))
            log.error(error)
            return error, http_code.BAD_REQUEST

        host_dict = request
        host_args = ['sure']
        result, errmsg = run_syscli1(
            'set', 'network', check_command_successful, *host_args, **host_dict)
        if not result:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            return error, http_code.INTERNAL_SERVER_ERROR

        response, qualifier, code = retrieve_host(host_dict)
        return response, http_code.ACCEPTED
    except Exception as e:
        error = dict(error=dict(message=getattr(
            e, 'message', str(e)), code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, http_code.INTERNAL_SERVER_ERROR


def retrieve_host(request):
    """
    Returns:
        response: model.network.HostPaginatedSchema
        qualifier: object
        code: HTTP Status Code

    Examples:
        {
            "DNS_Cache": "Disabled",
            "DNS_Servers": [{"DNS_Server": "172.16.0.10"}],
            "DefaultGateway": "10.10.1.1",
            "Domain": "localdomain",
            "Name": "dde1-2271"
        }

    """
    try:
        data, errmsg = run_syscli1('get', 'network', parse_config_style_raw)
        if errmsg or not data or not isinstance(data, list) or len(data) != 1:
            error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
            raise IguardApiWithCodeException(
                error=error, code=http_code.INTERNAL_SERVER_ERROR)
        return build_response(request, data[0])
    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, None, e.code
    except Exception as e:
        error = dict(error=dict(message=getattr(
            e, 'message', str(e)), code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, None, http_code.INTERNAL_SERVER_ERROR


def convert_from_request(in_data):
    if not in_data:
        raise ValidationError(
            'Need to have at least one attribute specified')
    # since the keys gets changed by attribute
    # note that a None key means that argument shouldn't be there
    # note that dns works because marshmallow is not loading to
    # {'DNS_Servers': [{'DNS_Server': 'ipaddr'}]} (marshmallow bug?)
    if in_data.get('dns_search_path', None):
        in_data['domain'] = (','.join(in_data.pop('dns_search_path')) if isinstance(in_data['dns_search_path'], list)
                             else in_data.pop('dns_search_path'))
    if in_data.get('dns_servers', None):
        in_data['dns'] = (','.join(in_data.pop('dns_servers')) if isinstance(in_data['dns_servers'], list)
                          else in_data.pop('dns_servers'))
    return in_data


def convert_to_response(out_data):
    if not out_data:
        return
    # since the keys gets changed by attribute
    # note that a None key means that argument shouldn't be there
    # note that dns works because marshmallow is not loading to
    # {'DNS_Servers': [{'DNS_Server': 'ipaddr'}]} (marshmallow bug?)
    dns_servers = [v for k, v in out_data.items() if k.startswith(
        'dns_') and k.endswith('_ip_address') and v]
    dns_search_path = [a.strip()
                       for a in out_data.get('dns_search_path', '').split(',')]
    out_data = {k: v for k, v in out_data.items() if not k.startswith(
        'dns_') and not k.endswith('_ip_address')}
    out_data['dns_servers'] = dns_servers
    out_data['dns_search_path'] = dns_search_path
    return out_data


# if extHostIp is set, set default gateway to this ip address by calling 'set network'
def set_default_gateway(intf_dict):
    response, qualifier, code = retrieve_host({})
    host_dict = convert_to_response(response['result'])
    host_dict = convert_from_request(host_dict)

    host_dict['defaultgateway'] = intf_dict['ipaddr']
    host_dict.pop('default_gateway', None)
    host_args = ['sure']

    result, errmsg = run_syscli1(
        'set', 'network', check_command_successful, *host_args, **host_dict)
    if not result:
        error = dict(error=dict(message=[errmsg], code='SYSTEM_ERROR'))
        raise IguardApiWithCodeException(
            error, http_code.INTERNAL_SERVER_ERROR)
