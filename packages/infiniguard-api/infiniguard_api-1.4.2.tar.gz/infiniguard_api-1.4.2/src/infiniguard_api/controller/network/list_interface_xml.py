import json
from collections import OrderedDict

import six
from dictdiffer import diff, patch
from infiniguard_api.lib import iguard_api_exceptions
from infiniguard_api.lib.hw.cli_handler import run_syscli1
from infiniguard_api.lib.hw.output_parser import parse_list_interface_xml
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.rest.pagination import Pagination
from infiniguard_api.model.netcfg_schemas import NetcfgPaginatedSchema
from infiniguard_api.lib.rest.common import http_code
from marshmallow import ValidationError, EXCLUDE

log = iguard_logging.get_logger(__name__)


def get_object_count(data):
    number_of_objects = len(data) if isinstance(
        data, list) else 1 if data else 0
    return number_of_objects


def build_metadata(request, data):
    number_of_objects = get_object_count(data) if isinstance(data, list) else 1
    pagination = Pagination(request.get('page_size', 50),
                            request.get('page', 1), number_of_objects)
    metadata = {
        'page_size': pagination.page_size,
        'page': pagination.page,
        'pages_total': pagination.pages,
        'number_of_objects': pagination.number_of_objects
    }
    return metadata


def build_response(request, data):
    try:
        metadata = build_metadata(request, data)
        response = dict(result=data, metadata=metadata)
        # print(json.dumps(response))
        return response, 'list' if request.get('name', None) is None else 'object', http_code.OK
    except ValidationError as e:
        error = dict(error=dict(message=e.messages, code=e.code))
        log.error(error)
        return error, None, http_code.INTERNAL_SERVER_ERROR
    except Exception as e:
        error = dict(error=dict(
            message=[getattr(e, 'message', str(e))], code='INTERNAL_SERVER_ERROR'))
        log.error(error)
        return error, None, http_code.INTERNAL_SERVER_ERROR


def list_interface_xml(request):
    """This function retrieves the netcfg by running syscli --list interface --xml. The returned data is
    then flattened by getting rid of unnecessary empty levels, and then validated against the netcfg
    schema. If the request dict has a name key for the intfname, then only data related to that interface
    is returned.

    Args:
        request: dict of the format request{'name'} or request{'errors'} if request validation failed.

    Returns:
        response: model.network.<XXX>PaginatedSchema or model.network.<XXX>PaginatedSchema, where XXX is one of:
            Host, Device(s), Bond(s), StaticRoute(s), LogicalInterface(s).
        qualifier: "object" or "list".
        code: HTTP status code.

    """
    try:
        result = get_netcfg()

        netcfg = transform_netcfg(result)

        netcfg = filter_netcfg(request, netcfg)
        return netcfg
    except Exception as e:
        raise iguard_api_exceptions.IguardApiException(
            'Bad netcfg (xml) from syscli. {}'.format(getattr(e, 'message', str(e))))


def get_netcfg():
    args = ['xml']
    result, errmsg = run_syscli1(
        'list', 'interface', parse_list_interface_xml, *args)
    if not result:
        error = dict(error=dict(
            message=[errmsg], code='INTERNAL_SERVER_ERROR'))
        raise iguard_api_exceptions.IguardApiException(error)
    return result


def transform_netcfg(result):
    netcfg = flatten(result)
    # print(json.dumps(netcfg))
    log.debug(json.dumps(netcfg))
    error = validate_data(netcfg, NetcfgPaginatedSchema)
    if error:
        raise iguard_api_exceptions.IguardApiException(error)
    return netcfg


def filter_netcfg(request, netcfg):
    name = request.get('name', None)
    if name:
        pintf = name.split(':')[0].split('.')[0]
        filter_by_devname(netcfg, pintf)
        if len(name.split(':')) > 1:
            for intf in ['ConfiguredInterfaces', 'RuntimeInterfaces']:
                netcfg[intf] = filter_by_vlanid_vintf(netcfg[intf], name)
    return netcfg


def filter_by_devname(netcfg, devname):
    netcfg.pop('Host', None)
    netcfg.pop('StaticRoutes', None)
    netcfg['CustomerInterfaces'] = [
        n for n in netcfg['CustomerInterfaces'] if n['Name'] == devname]
    netcfg['ConfiguredInterfaces'] = [
        n for n in netcfg['ConfiguredInterfaces'] if n['Name'] == devname]
    netcfg['RuntimeInterfaces'] = [
        n for n in netcfg['RuntimeInterfaces'] if n['Name'] == devname]


def filter_by_vlanid_vintf(intfs, full_devname):
    if len(intfs) != 1:
        return {}
    l3intfs = intfs[0]['L3Interfaces'] if intfs[0].get(
        'L3Interfaces') else None
    if not l3intfs:
        return {}
    if isinstance(l3intfs, list):
        l3intfs = [l3i for l3i in l3intfs if l3i['Name'] == full_devname]
        if len(intfs) == 1:
            intfs[0]['L3Interfaces'] = l3intfs
            return intfs
        else:
            raise iguard_api_exceptions.IguardApiException(
                'Bad L3 interface list: {}({})!'.format(intfs, full_devname))
    else:
        raise iguard_api_exceptions.IguardApiException(
            'Bad L3 interface list: {}!'.format(intfs))


def flatten_interfaces(interfaces):
    """Flattens a dict to remove dicts that have a nested dict with only one key

    Args:
        interfaces: [{..., 'Slaves': {'Slave': [{}] },
                    'L3Interfaces': {..., 'L3Interface': [{..., 'Segments': {'Segment': [{}] }}]}
                    }]

    Returns: [{..., 'Slave': [{}], 'L3Interface': [{ ..., 'Segment': [{}] }] }]
    """
    for i in interfaces:
        if i.get('Slaves'):
            i['Slaves'] = i['Slaves']['Slave']
        if i.get('L3Interfaces'):
            i['L3Interfaces'] = i['L3Interfaces']['L3Interface']
            for l in i.get('L3Interfaces'):
                # If someone manually configured IP, L3Interfaces:Segments will be None
                segments = l.get('Segment') or {'Segment':'ALL'}
                l['Segments'] = segments.get('Segment', 'ALL')
    return interfaces


def flatten(data):
    """Flattens a dict to remove keys that just have another dict with one key

    Args:
        data: {'Network': {
                    'Host': {},
                    'CustomerInterfaces': {
                        'CustomerInterface': [{}]}
                    },
                    'StaticRoutes': {
                        'StaticRoute': [{}]}
                    },
                    'ConfiguredInterfaces': {
                        'RuntimeInterface': [{}]}
                    }
                    'RuntimeInterfaces': {
                        'RuntimeInterface': [{}]}
                    }
                }
            }

    Returns: {'Host': {},
                'CustomerInterfaces': [{}]}
                'StaticRoutes': [{}]}
                'ConfiguredInterfaces': [{}]}
                'RuntimeInterfaces': [{}]}
            }
    """
    network = data['Network']
    network_cfg = OrderedDict()

    state = network['Configured_State']
    network_cfg['Host'] = state['Host']
    # network_cfg['Host'] = state.get('Host')
    # static_routes = state.get('StaticRoutes')
    # static_routes = static_routes['StaticRoutes'] if static_routes else None
    # network_cfg['StaticRoutes'] = static_routes.get('StaticRoute') if static_routes else None
    network_cfg['CustomerInterfaces'] = state['CustomerInterfaces']['CustomerInterface']
    network_cfg['ConfiguredInterfaces'] = flatten_interfaces(
        state['Interfaces']['Interface'])

    state = network['Runtime_State']
    network_cfg['StaticRoutes'] = state['StaticRoutes']['StaticRoute']
    # network_cfg['Host'] = state.get('Host')
    # static_routes = state.get('StaticRoutes')
    # static_routes = static_routes['StaticRoutes'] if static_routes else None
    # network_cfg['StaticRoutes'] = static_routes.get('StaticRoute') if static_routes else None
    network_cfg['RuntimeInterfaces'] = flatten_interfaces(
        state['Interfaces']['Interface'])

    return network_cfg


def validate_data(data, validation_schema):
    """Validates by loading data against the specified marshmallow schema.

    Args:
        data: Un-serialized data.
        validation_schema: Marshmallow schema to load against.

    Returns: an error dict on failure or None on success.

    """
    try:
        validation_schema(unknown=EXCLUDE, partial=True).load(data)
        return None
    except ValidationError as e:
        log.error(e.messages)
        errmsg = ['{}:{}'.format(k, v)
                  for (k, v) in e.messages.items()]
        error = dict(message=errmsg, code='WRONG_FIELD_VALUES')
        return error
    except Exception as e:
        log.error('{}'.format(e))
        error = dict(message=[getattr(e, 'message', str(e))], code='UNEXPECTED_VALIDATION_ERROR')
        return error
