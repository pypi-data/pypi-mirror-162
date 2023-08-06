from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.ost_schemas import (OstLsuCreateSchema,
                                               OstLsuEditSchema,
                                               OstLsusPaginatedSchema,
                                               OstLsuPaginatedSchema)

from infiniguard_api.controller.ost.lsu import (create_lsu,
                                                list_lsus,
                                                get_lsu,
                                                update_lsu,
                                                delete_lsu)

from flask import request

from infiniguard_api.view.ost import ost_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class LsusResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: OST Storage Servers
    """
    @ddoc
    @doc(operationId='list_lsus')
    @doc(params={'page_size':
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
                  'required': False}})
    @doc(params={'storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'storage_server',
                  'required': True}
                 })
    @marshal_with(OstLsusPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns all lsus for a given storage server
        """
        kwargs['storageserver'] = kwargs.pop('storage_server')
        response, code = list_lsus(kwargs, request.values)
        return (response, code)

    @ddoc
    @doc(operationId='create_lsu')
    @doc(params={'storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'storage_server',
                  'required': True}
                 })
    @use_kwargs(OstLsuCreateSchema(exclude=('storage_server',)))
    @marshal_with(OstLsuPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create lsu of a given storage server
        """
        kwargs['storageserver'] = kwargs.pop('storage_server')
        response, code = create_lsu(kwargs)
        return (response, code)


@ddoc
class LsuResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: OST Storage Servers
    """
    @ddoc
    @doc(operationId='get_lsu')
    @doc(params={'storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'storage_server',
                  'required': True}
                 })
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'lsu1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(OstLsuPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return LSU by name of a given storage server
        """
        response, code = get_lsu(kwargs['storage_server'], kwargs['name'])
        return (response, code)

    @ddoc
    @doc(operationId='update_lsu')
    @doc(params={'storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'storage_server',
                  'required': True}
                 })
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'lsu1',
                  'name': 'name',
                  'required': True}
                 })
    @use_kwargs(OstLsuEditSchema(exclude=('name',)))
    @marshal_with(OstLsuPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit LSU
        """
        kwargs['storageserver'] = kwargs.pop('storage_server')
        response, code = update_lsu(kwargs)
        return (response, code)

    @ddoc
    @doc(operationId='delete_lsu')
    @doc(params={'force':
                 {'in': 'query',
                  'description': 'Force delete LSU even if it contains files or backup images',
                  'type': 'boolean',
                  'required': False}})
    @doc(params={'storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'storage_server',
                  'required': True}
                 })
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'lsu1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete LSU
        """
        params = request.args
        force = params.get('force', 'False').upper()
        kwargs['storageserver'] = kwargs.pop('storage_server')
        response, code = delete_lsu(kwargs, force)
        return (response, code)


ost_lsu_view_func = LsuResource.as_view('lsu')
ost_lsus_view_func = LsusResource.as_view('lsus')

ost_api.add_url_rule(
    'storage_servers/<string:storage_server>/lsus/<string:name>',
    view_func=ost_lsu_view_func,
    methods=['GET', 'DELETE', 'PATCH'])

ost_api.add_url_rule(
    'storage_servers/<string:storage_server>/lsus/',
    view_func=ost_lsus_view_func,
    methods=['GET', 'POST'])
