from infiniguard_api.controller.network.netcfg import create_netcfg, delete_netcfg, retrieve_netcfg, update_netcfg
from flask_apispec import MethodResource, doc, marshal_with, use_kwargs
from infiniguard_api.model.netcfg_schemas import NetcfgCreateSchema, NetcfgPaginatedSchema
from infiniguard_api.view.network.common import network_api
from infiniguard_api.lib.documentation import ddoc


@ddoc
class NetcfgResource(MethodResource):
    """
    :Methods: POST, GET, PATCH, DELETE
    :Tags: Network configuration collection operations endpoint
    """

    @ddoc
    @use_kwargs(NetcfgCreateSchema)
    @marshal_with(NetcfgPaginatedSchema)
    def post(self, **kwargs):
        """
        :Summary: Create network configuration
        """
        response, code = create_netcfg(kwargs)
        return response, code

    @ddoc
    @doc(params=
         {
             'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
             'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}
         }
         )
    @marshal_with(NetcfgPaginatedSchema)
    def get(self, **kwargs):
        """
        :Summary: Displays the entire network configuration or for the specified device name
        """
        response, code = retrieve_netcfg(kwargs)
        return response, code

    @ddoc
    @use_kwargs(NetcfgCreateSchema(only=('mtu', 'mode', 'slaves', 'nat', 'extHostIp',)))
    @marshal_with(NetcfgPaginatedSchema)
    def patch(self, **kwargs):
        """
        :Summary: Update the network configuration for the specified device name
        """
        response, code = update_netcfg(kwargs)
        return response, code

    @doc(params=
         {'devname':
              {'in': 'query',
               'description': 'Device name',
               'type': 'string',
               'required': True}
          }
         )
    @marshal_with(NetcfgPaginatedSchema)
    def delete(self, **kwargs):
        """
        :Summary: Delete the network configuration for the specified device name
        """
        response, code = delete_netcfg(**kwargs)
        return response, code


netcfg_view_func = NetcfgResource.as_view('netcfg')

network_api.add_url_rule(
    'netcfg/',
    view_func=netcfg_view_func,
    methods=['POST', 'GET'])

network_api.add_url_rule(
    'netcfg/<string:devname>',
    view_func=netcfg_view_func,
    methods=['GET', 'PATCH', 'DELETE'])
