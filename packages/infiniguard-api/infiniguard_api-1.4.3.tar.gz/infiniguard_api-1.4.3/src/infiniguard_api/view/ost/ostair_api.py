from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.ost_schemas import (OstAirCreateSchema,
                                               OstLsuPaginatedSchema)

from infiniguard_api.controller.ost.ostair import (create_ostair,
                                                   update_ostair,
                                                   delete_ostair)

from infiniguard_api.view.ost import ost_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class OstairResource(MethodResource):
    """
    :Methods: POST, PATCH, DELETE
    :Tags: OST AIRs
    """
    @ddoc
    @use_kwargs(OstAirCreateSchema(exclude=('operation',)))
    @marshal_with(OstLsuPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create ost air
        """
        response, code = create_ostair(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'source_storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'source_storage_server',
                  'required': True}
                 })
    @doc(params={'source_lsu':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'lsu1',
                  'name': 'source_lsu',
                  'required': True}
                 })
    @use_kwargs(OstAirCreateSchema(exclude=('source_storage_server','source_lsu')))
    @marshal_with(OstLsuPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit ost air
        """
        kwargs['sourcess'] = kwargs.pop('source_storage_server')
        kwargs['sourcelsu'] = kwargs.pop('source_lsu')
        response, code = update_ostair(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'source_storage_server':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'server1',
                  'name': 'source_storage_server',
                  'required': True}
                 })
    @doc(params={'source_lsu':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'lsu1',
                  'name': 'source_lsu',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete ost air
        """
        kwargs['sourcess'] = kwargs.pop('source_storage_server')
        kwargs['sourcelsu'] = kwargs.pop('source_lsu')
        response, code = delete_ostair(kwargs)
        return (response, code)

ost_ostair_view_func = OstairResource.as_view('ostair')

ost_api.add_url_rule(
    'ostairs/',
    view_func=ost_ostair_view_func,
    methods=['POST'])

ost_api.add_url_rule(
    'ostairs/source_storage_servers/<string:source_storage_server>/source_lsus/<string:source_lsu>',
    view_func=ost_ostair_view_func,
    methods=['PATCH', 'DELETE'])
