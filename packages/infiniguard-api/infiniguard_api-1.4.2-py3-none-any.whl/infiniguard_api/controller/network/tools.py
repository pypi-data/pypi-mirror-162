import os
from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.lib.hw.cli_handler import run_syscli, run_python, execute_command
from infiniguard_api.lib.hw.netlib import (do_ping,
                                           do_traceroute,
                                           do_mtu,
                                           do_dig,
                                           do_resolv,
                                           get_interface_ethtool
                                           )
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.common import (build_paginated_response,
                                             build_error_message,
                                             build_error_model,
                                             build_entity_response,
                                             error_handler,
                                             build_async_task_response,
                                             validate_request_values
                                             )
from infiniguard_api.lib.rest.pagination import Pagination
from infiniguard_api.lib.hw.output_parser import parse_async
from infiniguard_api.model.models import (
    NetworkToolsInterfaceEthtoolLinkMode,
    NetworkToolsInterfaceStats,
    NetworkToolsInterface,
    NetworkToolsBondInterface,
    NetworkToolsInterfaceAddress,
    NetworkToolsInterfaceRoutes,
    NetworkToolsBondAdInfo,
    NetworkToolsResolvModel
)
from pyroute2 import IPRoute
from typing import List, Dict
log = iguard_logging.get_logger(__name__)


def convert_list_to_dict(data: List) -> Dict:
    keys = [x[0] for x in data]
    values = [x[1] for x in data]
    return dict(zip(keys, values))


@error_handler
def ping(**cli_dict):
    result = run_python(cli_dict, do_ping, 'do_ping')
    if not result:
        error = build_error_model(
            error_message=['Failed to run ping'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def mtu(**cli_dict):
    result = run_python(cli_dict, do_mtu, 'do_mtu')
    if not result:
        error = build_error_model(
            error_message=['Failed to run mtu'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def dig(**cli_dict):
    result = run_python(cli_dict, do_dig, 'do_dig')
    if not result:
        error = build_error_model(
            error_message=['Failed to run dig'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
def resolv(**cli_dict):
    nameservers, search_domain = do_resolv()
    data = {
        'nameservers': nameservers,
        'search_domain': search_domain
    }
    result = NetworkToolsResolvModel().import_data(data)
    return (build_paginated_response(
        result=result), http_code.OK)


@error_handler
def traceroute(**cli_dict):
    result = run_python(cli_dict, do_traceroute, 'do_traceroute')
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
    version = cli_dict.get('iperf_version', 1)
    dst = cli_dict.get('dst', None)
    src = cli_dict.get('src', None)
    parallel = cli_dict.get('parallel', None)
    time = cli_dict.get('time', None)
    buffer_len = cli_dict.get('buffer_len', None)
    reverse = cli_dict.get('reverse', None)

    if int(version) == 3:
        command_line = ['/usr/bin/iperf3', '-i', '1', '-c', dst]
    else:
        command_line = ['/usr/bin/iperf', '-i', '1', '-c', dst]
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
    result = run_syscli(command_line, parse_async, 'iperf')
    if not result:
        error = build_error_model(
            error_message=['Failed to run iperf'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED


@error_handler
@validate_request_values(['name', 'backend_ports'])
def interfaces_details(req, **kwargs):
    def bool_type(value):
        if value in ['true', 'True', 'TRUE', 'yes', 'y', 'Y', 'Yes', 'YES']:
            return True
        else:
            return False

    show_backend_ports = req.get('backend_ports', default=False, type=bool_type)
    per_page = req.get('page_size', default=50, type=int)
    page = req.get('page', default=1, type=int)
    interface_name = req.get('name', default='', type=str)

    interfaces = list()
    with IPRoute() as ipr:
        # This speeds things up drastically
        ipr.bind(async_cache=True)
        fields = {
            'ifname': 'IFLA_IFNAME',
            'state': '',
            'address': 'IFLA_ADDRESS',
            'phys_port_id': 'IFLA_PHYS_PORT_ID',
            'txqlen': 'IFLA_TXQLEN',
            'flags': '',
            'mtu': 'IFLA_MTU',
            'carrier': 'IFLA_CARRIER',
            'operstate': 'IFLA_OPERSTATE',
            'proto_down': 'IFLA_PROTO_DOWN',
            'promiscuity': 'IFLA_PROMISCUITY',
            'stats': 'IFLA_STATS64',
            'carrier_changes': 'IFLA_CARRIER_CHANGES',
            'index': '',
        }
        links = [a for a in ipr.get_links() if a.get('ifi_type') == 1]
        interfaces_dict = dict()
        for link in links:
            entry = dict()
            for key, value in fields.items():
                if value:
                    entry[key] = link.get_attr(value)
                else:
                    entry[key] = link.get(key)
            if link.get_attr('IFLA_LINKINFO'):
                entry['kind'] = link.get_attr(
                    'IFLA_LINKINFO').get_attr('IFLA_INFO_KIND')
            else:
                entry['kind'] = None
            entry['master'] = next((a.get_attr(
                'IFLA_IFNAME') for a in links if a['index'] == link.get_attr('IFLA_MASTER')), None)
            entry['state'] = entry['state'].upper()
            entry_name = entry.get('ifname')
            is_backend = entry_name.startswith('em')
            if not interface_name or entry_name == interface_name:
                if show_backend_ports or not is_backend:
                    interfaces_dict[entry_name] = entry

        # respond with 404 if interface name was not found in NDB records
        if len(interfaces_dict) == 0:
            error = build_error_model(
                error_message=[
                    'INTERFACE {} DOES NOT EXISTS'.format(interface_name)],
                error_code='NETWORK_TOOLS_INTERFACE_NOT_FOUND')
            return build_entity_response(error=error), http_code.NOT_FOUND
        try:
            for k, v in interfaces_dict.items():
                interface = NetworkToolsInterface().import_data(v)
                if not v['kind']:  # fetch ethtool link mode for non bond interfaces
                    speed, duplex, autoneg, port, supported_modes = get_interface_ethtool(
                        v['ifname'])
                    interface.speed = speed
                    interface.supported_modes = supported_modes
                    interface.supported_ports = port
                    interface.duplex = duplex
                    interface.autoneg = autoneg
                    interface.kind = 'port'

                elif v['kind'] == 'bond':
                    bond_data = [a.get_attr('IFLA_LINKINFO').get_attr(
                        'IFLA_INFO_DATA') for a in links if a.get('index') == v['index']][0]
                    bond_dict = convert_list_to_dict(bond_data.get('attrs'))
                    bond_properties = dict()
                    for key, value in bond_dict.items():
                        bond_properties[key[5:].lower()] = value
                    interface.bond_properties = NetworkToolsBondInterface(
                    ).import_data(bond_properties)
                    slave_ports = [a.get_attr('IFLA_IFNAME') for a in links if a.get_attr(
                        'IFLA_MASTER') == v['index']]
                    interface.bond_properties.bond_ports = slave_ports
                    if interface.bond_properties.bond_mode == 4:
                        bond_ad_info_dict = convert_list_to_dict(
                            bond_properties.get('bond_ad_info', {}).get('attrs', []))
                        bond_ad_info = NetworkToolsBondAdInfo().import_data(
                            bond_ad_info_dict)
                        interface.bond_properties.bond_ad_info = bond_ad_info
                    elif interface.bond_properties.bond_mode == 1:
                        active_slave_idx = interface.bond_properties.bond_active_slave
                        active_slave = next((x.get_attr('IFLA_IFNAME') for x in links
                                             if x['index'] == active_slave_idx), None)
                        interface.bond_properties.bond_active_slave = active_slave
                elif v['kind'] == 'vlan':
                    link = [a for a in links if a.get(
                        'index') == v['index']][0]
                    interface.vlan_id = link.get_attr('IFLA_LINKINFO') \
                        .get_attr('IFLA_INFO_DATA') \
                        .get_attr('IFLA_VLAN_ID')
                    interface.vlan_protocol = link.get_attr('IFLA_LINKINFO') \
                        .get_attr('IFLA_INFO_DATA') \
                        .get_attr('IFLA_VLAN_PROTOCOL')
                if k.startswith('em'):  # interface names starting with p marked as frontend
                    interface.backend_port = True

                ip_alias_fields = {
                    'label': 'IFA_LABEL',
                    'address': 'IFA_ADDRESS',
                    'prefixlen': '',
                    'broadcast': 'IFA_BROADCAST',
                }
                ip_aliases = []
                ip_aliases_records = [
                    a for a in ipr.get_addr() if a.get('index') == v['index'] and a.get('family') == 2]
                for ip_alias_record in ip_aliases_records:
                    entry = dict()
                    for key, value in ip_alias_fields.items():
                        if value:
                            entry[key] = ip_alias_record.get_attr(value)
                        else:
                            entry[key] = ip_alias_record.get(key)
                    ip_aliases.append(
                        NetworkToolsInterfaceAddress().import_data(entry))
                interface.ip_aliases = ip_aliases

                ip_route_fields = {
                    'dst': 'RTA_DST',
                    'dst_len': '',
                    'gateway': 'RTA_GATEWAY',
                    'family': '',
                    'prefsrc': 'RTA_PREFSRC',
                    'proto': '',
                    'table': '',
                    'type': ''
                }
                ip_routes = []
                ip_routes_records = [a for a in ipr.get_routes() if a.get(
                    'family') == 2 and a.get_attr('RTA_OIF') == v['index']]

                for ip_route_record in ip_routes_records:
                    entry = dict()
                    for key, value in ip_route_fields.items():
                        if value:
                            entry[key] = ip_route_record.get_attr(value)
                        else:
                            entry[key] = ip_route_record.get(key)
                    ip_routes.append(
                        NetworkToolsInterfaceRoutes().import_data(entry))

                interface.ip_routes = ip_routes
                interfaces.append(interface.to_primitive())
                log.debug(interface.to_primitive())
        except Exception as e:
            log.error('Failed to get network interfaces {}'.format(repr(e)))
    if not interfaces:
        error = build_error_model(
            error_message=['Failed to get network interfaces'],
            error_code='NETWORK_TOOLS_ERROR')
        return build_entity_response(error=error), http_code.INTERNAL_SERVER_ERROR

    total = len(interfaces)
    log.info("Total interfaces: {}".format(total))
    pagination = Pagination(per_page, page, total)
    metadata = {
        'page_size': per_page,
        'page': pagination.page,
        'pages_total': pagination.pages,
        'number_of_objects': total
    }
    result = interfaces[pagination.offset:pagination.offset + per_page]
    response = build_paginated_response(metadata=metadata, result=result)
    # log.debug(response)
    return response, http_code.OK
