from infiniguard_api.controller.network.list_interface_xml import log, list_interface_xml, build_response
from infiniguard_api.lib.iguard_api_exceptions import IguardApiWithCodeException
from marshmallow import ValidationError

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model, http_code)

def get_devices(request):
    """Endpoint:
        /network/devices/
        /network/devices/<name>

    CLI Command:
        syscli --list interface

    Args:
        request: dict of the format request{'name'} or request{'errors'} if request validation failed.

    Returns:
        response: model.network.DevicesPaginatedSchema or model.network.DevicePaginatedSchema
        qualifier: "object" or "list"
        code: HTTP Status Code

    Examples:
        [{"devname":"p1p1", "max_speed": "10GbE"}, {"devname":"p1p2", "max_speed": "10GbE"}, ...]
        [{"devname":"p1p1", "max_speed": "10GbE"}]

    """
    try:
        netcfg = list_interface_xml(request)

        is_collection = request.get('name', None) is None
        data = [d for d in netcfg['CustomerInterfaces'] if d['Name'].startswith('p')]
        data = data if is_collection else data[0] if len(data) == 1 else {}

        if not data and request.get('name', None):
            error = build_error_model(
                error_message=build_error_message({'get_devices': 'Device not found'}),
                error_code='DEVICE NOT_FOUND')
            return (build_entity_response(error=error), 'object', http_code.NOT_FOUND)
        return build_response(request, data)
    except ValidationError as e:
        error = build_error_model(
                error_message=build_error_message({'get_devices': e.messages}),
                error_code='BAD_REQUEST')
        return (build_entity_response(error=error), 'object', http_code.BAD_REQUEST)
        

    except IguardApiWithCodeException as e:
        log.error(e.error)
        return e.error, None, e.code
    except Exception as e:
        error = dict(error=dict(message=[getattr(e, 'message', str(e))], code='UNEXPECTED_EXCEPTION'))
        log.error(error)
        return error, None, http_code.INTERNAL_SERVER_ERROR
