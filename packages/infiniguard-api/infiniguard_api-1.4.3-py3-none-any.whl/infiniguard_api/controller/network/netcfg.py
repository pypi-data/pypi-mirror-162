# pragma: no cover
"""
Endpoint: /network/interfaces/
Methods: POST, GET, PATCH, DELETE
CLI Commands:
    syscli --backup netcfg
    syscli --restore netcfg [--sure]
"""

import json
from collections import OrderedDict

import six
from infiniguard_api.common import messages
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import check_command_successful, parse_list_interface_xml
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import build_error_message
from infiniguard_api.lib.rest.pagination import Pagination
from infiniguard_api.model.netcfg_schemas import NetcfgPaginatedSchema
from marshmallow import ValidationError

log = iguard_logging.get_logger(__name__)


def filter_by_vlanid_vintf(intfs, full_devname):
    if len(intfs) != 1:
        return {}
    l3intf = intfs[0]['L3Interfaces'] if intfs[0].get('L3Interfaces') else None
    if not l3intf:
        return {}
    if isinstance(l3intf, list) and [l3i for l3i in l3intf if l3i['Name'] == full_devname]:
        return intfs
    return {}


def filter_by_devname(result, devname):
    # filter out customer, configured and running interfaces by dev_name
    netcfg = result['NetworkCfg']
    netcfg.pop('Host', None)
    netcfg.pop('StaticRoutes', None)
    netcfg['CustomerInterfaces'] = [n for n in netcfg['CustomerInterfaces'] if n['Name'] == devname]
    netcfg['ConfiguredInterfaces'] = [n for n in netcfg['ConfiguredInterfaces'] if n['Name'] == devname]
    netcfg['RuntimeInterfaces'] = [n for n in netcfg['RuntimeInterfaces'] if n['Name'] == devname]


def validate_data(data, validation_schema):
    try:
        validation_schema().load(data)
        return None
    except ValidationError as e:
        log.error(e.message)
        errmsg = ['{}:{}'.format(k, v) for error in e.values() for (k, v) in error.items()]
        error = dict(message=errmsg, code='WRONG_FIELD_VALUES')
        return error
    except Exception as e:
        log.error(e.message)
        error = dict(message=e.message, code='UNEXPECTED_VALIDATION_ERROR')
        return error


# syscli --add netcfg --devname <DEVNAME> [--dhcp] |[--ipaddr <IPADDR> --netmask <NETMASK>
# --gateway <GATEWAY>] [--slaves <DEV1>,<DEV2>,<...>] [--mode RR|AB|LACP] [--mtu <SIZE>]
# [--defaultgw YES] [--segments REP,MGMT,DATA] [--nat <NAT_IPADDR>] [--hosts <IP1,IP2,IP3>]
# [--extHostIp YES] [--sure]
def create_netcfg(response):
    try:
        if response['errors']:
            error = dict(error=dict(message=build_error_message(response['errors']), code='WRONG_FIELD_VALUES'))
            log.error(error)
            return error, 400

        netcfg_dict = response['data']
        netcfg_args = ['dhcp', 'sure'] if netcfg_dict.pop('dhcp', None) else ['sure']
        result, errmsg = run_syscli1('add', 'netcfg', check_command_successful, *netcfg_args, **netcfg_dict)
        if not result:
            error = dict(error=dict(message=[errmsg], code='WRONG_FIELD_VALUES'))
            return error, 400

        data, code = retrieve_netcfg(netcfg_dict)
        data['message'] = messages.DDE_REBOOT_MSG
        return data, 201
    except Exception as e:
        error = dict(error=dict(message=e.message, code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, 400


def retrieve_netcfg(response):
    try:
        if response.get('errors', None):
            error = dict(error=dict(message=build_error_message(response['errors']), code='BAD_ARGUMENTS'))
            log.error(error)
            return error, 400

        args = ['xml']
        result, errmsg = run_syscli1('list', 'interface', parse_list_interface_xml, *args)
        if not result:
            error = dict(error=dict(message=[errmsg], code='ERROR_RETRIEVING_DATA'))
            return error, 400

        network_cfg = flatten(result)
        log.debug(json.dumps(network_cfg))
        error = validate_data(network_cfg, NetcfgPaginatedSchema)
        if error:
            return dict(error=error), 400

        devname = response.get('devname', None)
        if devname:
            pintf = devname.split(':')[0].split('.')[0]
            filter_by_devname(network_cfg, pintf)
            if len(devname.split(':')) > 1:
                for intf in ['ConfiguredInterfaces', 'RuntimeInterfaces']:
                    network_cfg['NetworkCfg'][intf] = filter_by_vlanid_vintf(network_cfg['NetworkCfg'][intf], devname)

        pagination = Pagination(response.get('page_size', 50), response.get('page', 1), len(network_cfg))
        metadata = {
            'page_size': pagination.page_size,
            'page': pagination.page,
            'pages_total': pagination.pages,
            'number_of_objects': pagination.number_of_objects
        }

        response = dict(result=network_cfg, metadata=metadata)
        return response, 200
    except Exception as e:
        error = dict(error=dict(message=e.message, code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, 400


def update_netcfg(response):
    try:
        if response['errors']:
            error = dict(error=dict(message=build_error_message(response['errors']), code='WRONG_FIELD_VALUES'))
            log.error(error)
            return error, 400

        devname = response.get('devname', None)
        if not response.get('data', {}) or not response['data']:
            error = dict(error=dict(message=messages.CHANGE_SPECIFIED_IN_BODY, code='NO_FIELD_VALUES'))
            log.error(error)
            return error, 400

        netcfg_args = ['sure']
        response['devname'] = devname
        netcfg_dict = response['data']

        result, errmsg = run_syscli1('edit', 'netcfg', check_command_successful, *netcfg_args, **netcfg_dict)
        if not result:
            error = dict(error=dict(message=[errmsg], code='WRONG_FIELD_VALUES'))
            return error, 400

        data, code = retrieve_netcfg(netcfg_dict)
        data['message'] = messages.DDE_REBOOT_MSG
        return data, 200
    except Exception as e:
        error = dict(error=dict(message=e.message, code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, 400


def delete_netcfg(devname=None):
    try:
        netcfg_args = ['sure']
        netcfg_kwargs = {'devname': devname}
        result, errmsg = run_syscli1('del', 'netcfg', check_command_successful, *netcfg_args, **netcfg_kwargs)
        if not result:
            error = dict(message=[errmsg], code='WRONG_FIELD_VALUES')
            return dict(error=error), 400

        data = dict(message=messages.DDE_REBOOT_MSG)
        return data, 200
    except Exception as e:
        error = dict(error=dict(message=e.message, code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, 400


def flatten_interfaces(interfaces):
    for i in interfaces:
        if i.get('Slaves'):
            i['Slaves'] = i['Slaves']['Slave']
        if i.get('L3Interfaces'):
            i['L3Interfaces'] = i['L3Interfaces']['L3Interface']
            for l in i.get('L3Interfaces'):
                l['Segments'] = l['Segments']['Segment']
    return interfaces


def flatten(data):
    network = data['Network']

    network_cfg = OrderedDict()

    state = network['Configured_State']
    network_cfg['Host'] = state['Host']
    network_cfg['CustomerInterfaces'] = state['CustomerInterfaces']['CustomerInterface']
    network_cfg['ConfiguredInterfaces'] = flatten_interfaces(state['Interfaces']['Interface'])

    state = network['Runtime_State']
    network_cfg['StaticRoutes'] = state['StaticRoutes']['StaticRoute']
    network_cfg['RuntimeInterfaces'] = flatten_interfaces(state['Interfaces']['Interface'])

    return OrderedDict({'NetworkCfg': network_cfg})


if __name__ == '__main__':
    with open('../tst/responses/netcfg.json') as fp:
        result = json.loads(fp.read())
    data = flatten(result)
    print((json.dumps(data)))
