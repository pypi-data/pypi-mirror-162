from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.ost_schemas import (OstStorageserverCreateSchema,
                                               OstStorageserversPaginatedSchema,
                                               OstStorageserverPaginatedSchema)

from infiniguard_api.controller.ost.storageserver import (create_storageserver,
                                               list_storageservers,
                                               update_storageserver,
                                               delete_storageserver,
                                               get_storageserver)

from flask import request

from infiniguard_api.view.ost import ost_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class StorageserversResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: OST Storage Servers
    """
    @ddoc
    @doc(operationId='list_storageservers')
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
    @marshal_with(OstStorageserversPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the configuration for all storage servers
        """
        response, code = list_storageservers(kwargs, request.values)
        return (response, code)

    @ddoc
    @doc(operationId='create_storageserver')
    @use_kwargs(OstStorageserverCreateSchema)
    @marshal_with(OstStorageserverPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create storage server
        """ 
        response, code = create_storageserver(kwargs)
        return (response, code)

@ddoc
class StorageserverResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: OST Storage Servers
    """
    @ddoc
    @doc(operationId='get_storageserver')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(OstStorageserverPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return storage server by name
        """
        response, code = get_storageserver(kwargs['name'])
        return (response, code)

    @ddoc
    @doc(operationId='update_storageserver')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'name',
                  'required': True}
                 })
    @use_kwargs(OstStorageserverCreateSchema(exclude=('name',)))
    @marshal_with(OstStorageserverPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit storage server
        """
        response, code = update_storageserver(kwargs)
        return (response, code)

    @ddoc
    @doc(operationId='delete_storageserver')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete storage server
        """
        response, code = delete_storageserver(kwargs['name'])
        return (response, code)

ost_storageserver_view_func = StorageserverResource.as_view('storageserver')
ost_storageservers_view_func = StorageserversResource.as_view('storageservers')

ost_api.add_url_rule(
    'storage_servers/<string:name>',
    view_func=ost_storageserver_view_func,
    methods=['GET', 'PATCH', 'DELETE'])

ost_api.add_url_rule(
    'storage_servers/',
    view_func=ost_storageservers_view_func,
    methods=['GET', 'POST'])
