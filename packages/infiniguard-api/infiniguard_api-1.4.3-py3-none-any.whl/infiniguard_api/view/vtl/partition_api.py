from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlPartitionCreateSchema,
                                               VtlPartitionEditSchema,
                                               VtlPartitionsPaginatedSchema,
                                               VtlPartitionPaginatedSchema,
                                               VtlPartitionDevicesPaginatedSchema,
                                               VtlPartitionStorageLocationsPaginatedSchema)

from infiniguard_api.controller.vtl.partition import (create_partition,
                                               list_partitions,
                                               update_partition,
                                               delete_partition,
                                               get_partition,
                                               get_partition_devices,
                                               get_partition_storage_locations,
                                               set_partition_offline,
                                               set_partition_online)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class PartitionsResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='list_partitions')
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
    @marshal_with(VtlPartitionsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the configuration for all partitions
        """
        response, code = list_partitions(kwargs, request.values)
        return (response, code)

    @ddoc
    @doc(operationId='create_partition')
    @use_kwargs(VtlPartitionCreateSchema)
    @marshal_with(VtlPartitionPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create partition
        """ 
        response, code = create_partition(kwargs)
        return (response, code)

@ddoc
class PartitionsOfflineResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='partitions_offline')
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Set all partitions offline
        """
        response, code = set_partition_offline()
        return (response, code)

@ddoc
class PartitionsOnlineResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='partitions_online')
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Set all partitions online
        """
        response, code = set_partition_online()
        return (response, code)

@ddoc
class PartitionResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='get_partition')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(VtlPartitionPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return partition by name
        """
        response, code = get_partition(kwargs['par_name'])
        return (response, code)

    @ddoc
    @doc(operationId='update_partition')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partiton1',
                  'name': 'par_name',
                  'required': True}
                 })
    @use_kwargs(VtlPartitionEditSchema(exclude=('name',)))
    @marshal_with(VtlPartitionPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit partiton
        """
        response, code = update_partition(kwargs)
        return (response, code)

    @ddoc
    @doc(operationId='delete_partition')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete partition
        """
        response, code = delete_partition(kwargs['par_name'])
        return (response, code)

@ddoc
class PartitionOfflineResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='partition_offline')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Set partition offline
        """
        response, code = set_partition_offline(kwargs['par_name'])
        return (response, code)

@ddoc
class PartitionOnlineResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='partition_online')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Set partition offline
        """
        response, code = set_partition_online(kwargs['par_name'])
        return (response, code)

@ddoc
class PartitionDevicesResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='get_partition_devices')
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
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(VtlPartitionDevicesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return partition devices by partition name
        """
        kwargs['name'] = kwargs.pop('par_name')
        response, code = get_partition_devices(kwargs, request.values)
        return (response, code)

@ddoc
class PartitionSourceStorageLocationsResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='get_partition_source_storage_locations')
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
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(VtlPartitionStorageLocationsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return partition devices by partition name
        """
        kwargs['name'] = kwargs.pop('par_name')
        kwargs['loc'] = 'source'
        response, code = get_partition_storage_locations(kwargs, request.values)
        return (response, code)

@ddoc
class PartitionDestStorageLocationsResource(MethodResource):
    """
    :Methods: GET
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='get_partition_dest_storage_locations')
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
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'partition1',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(VtlPartitionStorageLocationsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return partition devices by partition name
        """
        kwargs['name'] = kwargs.pop('par_name')
        kwargs['loc'] = 'dest'
        response, code = get_partition_storage_locations(kwargs, request.values)
        return (response, code)

vtl_partition_view_func = PartitionResource.as_view('partition')
vtl_partition_offline_view_func = PartitionOfflineResource.as_view('partition_offline')
vtl_partition_online_view_func = PartitionOnlineResource.as_view('partition_online')
vtl_partitions_view_func = PartitionsResource.as_view('partitions')
vtl_partitions_offline_view_func = PartitionsOfflineResource.as_view('partitions_offline')
vtl_partitions_online_view_func = PartitionsOnlineResource.as_view('partitions_online')
vtl_partition_devices_view_func = PartitionDevicesResource.as_view('partition_devices')
vtl_partition_source_storage_locations_view_func = PartitionSourceStorageLocationsResource.as_view('partition_source_storage_locations')
vtl_partition_dest_storage_locations_view_func = PartitionDestStorageLocationsResource.as_view('partition_dest_storage_locations')

vtl_api.add_url_rule(
    'partitions/<string:par_name>',
    view_func=vtl_partition_view_func,
    methods=['GET', 'PATCH', 'DELETE'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/offline',
    view_func=vtl_partition_offline_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/online',
    view_func=vtl_partition_online_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/',
    view_func=vtl_partitions_view_func,
    methods=['GET', 'POST'])

vtl_api.add_url_rule(
    'partitions/offline',
    view_func=vtl_partitions_offline_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/online',
    view_func=vtl_partitions_online_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/devices',
    view_func=vtl_partition_devices_view_func,
    methods=['GET'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/source_storage_locations',
    view_func=vtl_partition_source_storage_locations_view_func,
    methods=['GET'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/dest_storage_locations',
    view_func=vtl_partition_dest_storage_locations_view_func,
    methods=['GET'])