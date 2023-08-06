from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.vtl_schemas import (VtlMediaCreateSchema,
                                               VtlMediaUnloadSchema,
                                               VtlMediaMoveSchema,
                                               VtlMediasPaginatedSchema,
                                               VtlMediaPaginatedSchema)

from infiniguard_api.model.task_schemas import (TaskSchema)

from infiniguard_api.controller.vtl.media import (create_media,
                                                  list_media,
                                                  move_media,
                                                  delete_all_media,
                                                  get_media,
                                                  delete_media,
                                                  import_media,
                                                  export_media,
                                                  write_protect_media,
                                                  recycle_media,
                                                  unload_media)

from flask import request

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class MediasResource(MethodResource):
    """
    :Methods: GET, POST, DELETE
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='list_medias')
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
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(VtlMediasPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns all medias for a given partition
        """
        kwargs['name'] = kwargs.pop('par_name')
        response, code = list_media(kwargs, request.values)
        return (response, code)

    @ddoc
    @doc(operationId='create_media')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @use_kwargs(VtlMediaCreateSchema(exclude=('name',)))
    @marshal_with(VtlMediasPaginatedSchema, code=http_code.CREATED)
    @marshal_with(TaskSchema, code=http_code.ACCEPTED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create one of more media of a given partition
        """
        kwargs['name'] = kwargs.pop('par_name')
        response, code = create_media(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete all media
        """
        kwargs.pop('par_name')
        kwargs['name'] = '*UNASSIGNED'
        response, code = delete_all_media(kwargs)
        return (response, code)

@ddoc
class MediasImportResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='medias_import')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Import all media
        """
        name = kwargs.pop('par_name')
        response, code = import_media(name, None)
        return (response, code)

@ddoc
class MediasExportResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='medias_export')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Export all media
        """
        name = kwargs.pop('par_name')
        response, code = export_media(name, None)
        return (response, code)

@ddoc
class MediasWriteProtectEnableResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='medias_write_protect_enable')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Enable write protect for all media
        """
        name = kwargs.pop('par_name')
        response, code = write_protect_media(name, None, False)
        return (response, code)

@ddoc
class MediasWriteProtectDisableResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='medias_write_protect_disable')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Disable write protect for all media
        """
        name = kwargs.pop('par_name')
        response, code = write_protect_media(name, None, True)
        return (response, code)

@ddoc
class MediasRecycleResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='medias_recycle')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Recycle all media
        """
        name = kwargs.pop('par_name')
        response, code = recycle_media(name, None)
        return (response, code)

@ddoc
class MediasMoveResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='medias_move')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @use_kwargs(VtlMediaMoveSchema(exclude=('name',)))
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Move media
        """
        kwargs['name'] = kwargs.pop('par_name')
        response, code = move_media(kwargs)
        return (response, code)

@ddoc
class MediaResource(MethodResource):
    """
    :Methods: GET, DELETE
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='get_media')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(VtlMediaPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return media by barcode of a given partition
        """
        response, code = get_media(kwargs['par_name'], kwargs['barcode'])
        return (response, code)

    @ddoc
    @doc(operationId='delete_media')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete Media
        """
        kwargs.pop('par_name')
        kwargs['name'] = '*UNASSIGNED'
        response, code = delete_media(kwargs)
        return (response, code)

@ddoc
class MediaImportResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='media_import')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Import media
        """
        name = kwargs.pop('par_name')
        barcode = kwargs.pop('barcode', None)
        response, code = import_media(name, barcode)
        return (response, code)

@ddoc
class MediaExportResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='media_export')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Export media
        """
        name = kwargs.pop('par_name')
        barcode = kwargs.pop('barcode', None)
        response, code = export_media(name, barcode)
        return (response, code)

@ddoc
class MediaWriteProtectEnableResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='media_write_protect_enable')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Enable write protect on media
        """
        name = kwargs.pop('par_name')
        barcode = kwargs.pop('barcode', None)
        response, code = write_protect_media(name, barcode, False)
        return (response, code)

@ddoc
class MediaWriteProtectDisableResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='media_write_protect_disable')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Disable write protect on media
        """
        name = kwargs.pop('par_name')
        barcode = kwargs.pop('barcode', None)
        response, code = write_protect_media(name, barcode, True)
        return (response, code)

@ddoc
class MediaRecycleResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='media_recycle')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Recycle media
        """
        name = kwargs.pop('par_name')
        barcode = kwargs.pop('barcode', None)
        response, code = recycle_media(name, barcode)
        return (response, code)

@ddoc
class MediaUnloadResource(MethodResource):
    """
    :Methods: POST
    :Tags: VTL Partitions & Media & Hostmapping
    """
    @ddoc
    @doc(operationId='media_unload')
    @doc(params={'par_name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'myvtl',
                  'name': 'par_name',
                  'required': True}
                 })
    @doc(params={'barcode':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'SDL101',
                  'name': 'barcode',
                  'required': True}
                 })
    @use_kwargs(VtlMediaUnloadSchema(exclude=('barcode','loctype','index',)))
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Unload media
        """
        kwargs['name'] = kwargs.pop('par_name')
        kwargs['barcode'] = kwargs.pop('barcode')
        response, code = unload_media(kwargs)
        return (response, code)

vtl_media_view_func = MediaResource.as_view('media')
vtl_media_import_view_func = MediaImportResource.as_view('media_import')
vtl_media_export_view_func = MediaExportResource.as_view('media_export')
vtl_media_write_protect_enable_view_func = MediaWriteProtectEnableResource.as_view('media_write_protect_enable')
vtl_media_write_protect_disable_view_func = MediaWriteProtectDisableResource.as_view('media_write_protect_disable')
vtl_media_recycle_view_func = MediaRecycleResource.as_view('media_recycle')
vtl_media_unload_view_func = MediaUnloadResource.as_view('media_unload')
vtl_medias_view_func = MediasResource.as_view('medias')
vtl_medias_import_view_func = MediasImportResource.as_view('medias_import')
vtl_medias_export_view_func = MediasExportResource.as_view('medias_export')
vtl_medias_write_protect_enable_view_func = MediasWriteProtectEnableResource.as_view('medias_write_protect_enable')
vtl_medias_write_protect_disable_view_func = MediasWriteProtectDisableResource.as_view('medias_write_protect_disable')
vtl_medias_recycle_view_func = MediasRecycleResource.as_view('medias_recycle')
vtl_medias_move_view_func = MediasMoveResource.as_view('medias_move')

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>',
    view_func=vtl_media_view_func,
    methods=['GET', 'DELETE'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>/import',
    view_func=vtl_media_import_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>/export',
    view_func=vtl_media_export_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>/write_protect_enable',
    view_func=vtl_media_write_protect_enable_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>/write_protect_disable',
    view_func=vtl_media_write_protect_disable_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>/recycle',
    view_func=vtl_media_recycle_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/<string:barcode>/unload',
    view_func=vtl_media_unload_view_func,
    methods=['POST'])
vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/',
    view_func=vtl_medias_view_func,
    methods=['GET', 'POST', 'DELETE'])
vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/import',
    view_func=vtl_medias_import_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/export',
    view_func=vtl_medias_export_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/write_protect_enable',
    view_func=vtl_medias_write_protect_enable_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/write_protect_disable',
    view_func=vtl_medias_write_protect_disable_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/recycle',
    view_func=vtl_medias_recycle_view_func,
    methods=['POST'])

vtl_api.add_url_rule(
    'partitions/<string:par_name>/media/move',
    view_func=vtl_medias_move_view_func,
    methods=['POST'])