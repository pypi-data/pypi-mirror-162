from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.replication_schemas import (OstMappingCreateSchema,
                                                       OstMappingsPaginatedSchema,
                                                       OstMappingPaginatedSchema)

from infiniguard_api.controller.replication.ostmapping import (create_ostmapping,
                                                               list_ostmappings,
                                                               update_ostmapping,
                                                               delete_ostmapping,
                                                               get_ostmapping)

from flask import request

from infiniguard_api.view.replication import replication_api

@doc(tags=['OST Replication'])
class OstMappingsResource(MethodResource):
    """
    Methods: GET, POST
    """
    @marshal_with(OstMappingsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        List ost replication target mapping
        """
        response, code = list_ostmappings(kwargs, request.values)
        return (response, code)

    @use_kwargs(OstMappingCreateSchema)
    @marshal_with(OstMappingPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        response, code = create_ostmapping(kwargs)
        return (response, code)

@doc(tags=['OST Replication'])
class OstMappingResource(MethodResource):
    """
    Methods: GET, PATCH, DELETE
    """
    @marshal_with(OstMappingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        Get OST replication mapping by target ip
        """
        response, code = get_ostmapping(kwargs)
        return (response, code)

    @use_kwargs(OstMappingCreateSchema(exclude=('dataip',)))
    @marshal_with(OstMappingPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        response, code = update_ostmapping(kwargs)
        return (response, code)

    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        response, code = delete_ostmapping(kwargs['dataip'])
        return (response, code)

ost_mapping_view_func = OstMappingResource.as_view('ostmapping')
ost_mappings_view_func = OstMappingsResource.as_view('ostmappings')

replication_api.add_url_rule(
    'ostmappings/<string:dataip>',
    view_func=ost_mapping_view_func,
    methods=['GET', 'PATCH', 'DELETE'])

replication_api.add_url_rule(
    'ostmappings/',
    view_func=ost_mappings_view_func,
    methods=['GET', 'POST'])
