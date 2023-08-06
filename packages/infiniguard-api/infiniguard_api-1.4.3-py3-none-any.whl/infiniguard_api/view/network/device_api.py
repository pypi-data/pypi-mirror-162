from infiniguard_api.common.messages import paginated_params_desc
from infiniguard_api.controller.network.devices import get_devices
from flask_apispec import MethodResource, doc, marshal_with
from infiniguard_api.model.network import DeviceResponse, DevicesResponse
from infiniguard_api.view.network.common import network_api
from infiniguard_api.model.base_schema import ErrorResponseSchema
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc


@ddoc
class DevicesResource(MethodResource):
    """
    :Methods: GET
    :Tags: Network Devices
    """
    @ddoc
    @doc(operationId='get_devices')
    @doc(params=paginated_params_desc)
    @marshal_with(DevicesResponse, code=http_code.OK, description="DevicesResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the configuration for all devices
        """
        response, qualifier, code = get_devices(kwargs)
        return response, code


@ddoc
class DeviceResource(MethodResource):
    """
    :Methods: GET
    :Tags: Network Devices
    """
    @ddoc
    @doc(operationId='get_device')
    @doc(params=paginated_params_desc)
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'dev0',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(DeviceResponse, code=http_code.OK, description="DeviceResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the configuration for a specific device
        """
        response, qualifier, code = get_devices(kwargs)
        return (response, code)


devices_view_func = DevicesResource.as_view('devices')
device_view_func = DeviceResource.as_view('device')

network_api.add_url_rule(
    'devices/', view_func=devices_view_func, methods=['GET'])
network_api.add_url_rule('devices/<string:name>',
                         view_func=device_view_func, methods=['GET'])
