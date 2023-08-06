from infiniguard_api.common.messages import paginated_params_desc
from infiniguard_api.controller.network.static_routes import (create_static_route, delete_static_route,
                                                              retrieve_static_routes)
from flask_apispec import (MethodResource,
                                                                 doc,
                                                                 marshal_with,
                                                                 use_kwargs)
from infiniguard_api.model.network import (StaticRouteResponse, StaticRouteSchema, StaticRoutesResponse)
from infiniguard_api.view.network.common import network_api
from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc


@ddoc
class StaticRoutesResource(MethodResource):
    """
    :Methods: POST,GET
    :Tags: Static Routes
    """

    @ddoc
    @doc(operationId='create_route')
    @use_kwargs(StaticRouteSchema)
    @marshal_with(StaticRouteResponse, code=http_code.ACCEPTED, description="StaticRouteResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create static route
        """
        response, code = create_static_route(kwargs)
        return response, code

    @ddoc
    @doc(operationId='get_routes')
    @doc(params=paginated_params_desc)
    @doc(summary='Returns all static routes by devname', params={'devname':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4',
                  'name': 'devname',
                  'required': True}
                 })
    @marshal_with(StaticRoutesResponse, code=http_code.OK, description="StaticRoutesResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns all static routes
        """
        response, qualifier, code = retrieve_static_routes(kwargs)
        return response, code


@ddoc
class StaticRoutesResourceDevname(MethodResource):
    """
    :Methods: POST,GET
    :Tags: Static Routes
    """

    @ddoc
    @doc(operationId='create_route_devname')
    @use_kwargs(StaticRouteSchema)
    @marshal_with(StaticRouteResponse, code=http_code.ACCEPTED, description="StaticRouteResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create static route
        """
        response, code = create_static_route(kwargs)
        return response, code

    @ddoc
    @doc(operationId='get_routes_devname')
    @doc(params=paginated_params_desc)
    @doc(summary='Returns all static routes by devname', params={'devname':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4',
                  'name': 'devname',
                  'required': True}
                 })
    @marshal_with(StaticRoutesResponse, code=http_code.OK, description="StaticRoutesResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns all static routes
        """
        response, qualifier, code = retrieve_static_routes(kwargs)
        return response, code


@ddoc
class StaticRouteResource(MethodResource):
    """
    :Methods: GET,DELETE
    :Tags: Static Routes
    """

    @ddoc
    @doc(operationId='get_routes_by_ip')
    @doc(params=paginated_params_desc)
    @doc(params={'network':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '10.10.10.0',
                  'name': 'network',
                  'required': True}
                 })
    @doc(params={'devname':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4',
                  'name': 'devname',
                  'required': True}
                 })
    @marshal_with(StaticRouteResponse, code=http_code.OK, description="StaticRouteResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the static routes with the specified IP address
        """
        response, qualifier, code = retrieve_static_routes(kwargs)
        return response, code

    @ddoc
    @doc(operationId='delete_routes')
    @doc(params={'network':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '10.10.10.0',
                  'name': 'network',
                  'required': True}
                 })
    @doc(params={'devname':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4',
                  'name': 'devname',
                  'required': True}
                 })
    @marshal_with(MessageSchema, http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete the static route with the specified ip address
        """
        response, code = delete_static_route(kwargs)
        return response, code


@ddoc
class StaticRouteResourceDevname(StaticRouteResource):
    """
    :Methods: GET,DELETE
    :Tags: Static Routes
    """

    @ddoc
    @doc(operationId='get_routes_by_ip_devname')
    @doc(params=paginated_params_desc)
    @doc(params={'network':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '10.10.10.0',
                  'name': 'network',
                  'required': True}
                 })
    @doc(params={'devname':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4',
                  'name': 'devname',
                  'required': True}
                 })
    @marshal_with(StaticRouteResponse, code=http_code.OK, description="StaticRouteResponse on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the static routes with the specified IP address
        """
        response, qualifier, code = retrieve_static_routes(kwargs)
        return response, code

    @ddoc
    @doc(operationId='delete_routes_devname')
    @doc(params={'network':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '10.10.10.0',
                  'name': 'network',
                  'required': True}
                 })
    @doc(params={'devname':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'p4p4',
                  'name': 'devname',
                  'required': True}
                 })
    @marshal_with(MessageSchema, http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete the static route with the specified ip address
        """
        response, code = delete_static_route(kwargs)
        return response, code


static_routes_view_func = StaticRoutesResource.as_view('static_routes')
static_routes_devname_view_func = StaticRoutesResourceDevname.as_view('static_routes_devname')
static_route_view_func = StaticRouteResource.as_view('static_route')
static_route_devname_view_func = StaticRouteResourceDevname.as_view('static_route_devname')

network_api.add_url_rule('static_routes/', view_func=static_routes_view_func, methods=['POST', 'GET'])
network_api.add_url_rule('static_routes/devices/<string:devname>', view_func=static_routes_devname_view_func, methods=['GET'])
network_api.add_url_rule('static_routes/<string:network>', view_func=static_route_view_func, methods=['GET', 'DELETE'])
network_api.add_url_rule('static_routes/<string:network>/devices/<string:devname>', view_func=static_route_devname_view_func, methods=['GET', 'DELETE'])
