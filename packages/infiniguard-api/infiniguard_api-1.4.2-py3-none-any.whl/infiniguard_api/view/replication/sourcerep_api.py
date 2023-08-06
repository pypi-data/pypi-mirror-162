from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.replication_schemas import (ReplicationSourceCreateSchema,
                                                       ReplicationSourcesPaginatedSchema,
                                                       ReplicationSourcePaginatedSchema)

from infiniguard_api.controller.replication.sourcerep import (create_sourcerep,
                                                              list_sourcereps,
                                                              delete_sourcerep,
                                                              get_sourcerep)

from flask import request

from infiniguard_api.view.replication import replication_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class SourcerepsResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: OST Replication

    """
    @ddoc
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
    @marshal_with(ReplicationSourcesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the configuration for all replication sources
        """
        response, code = list_sourcereps(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(ReplicationSourceCreateSchema)
    @marshal_with(ReplicationSourcePaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create replication source
        """
        response, code = create_sourcerep(kwargs)
        return (response, code)

@ddoc
class SourcerepResource(MethodResource):
    """
    :Methods: GET, DELETE
    :Tags: OST Replication
    """
    @ddoc
    @doc(params={'hostid':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'host1',
                  'name': 'hostid',
                  'required': True}
                 })
    @marshal_with(ReplicationSourcePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return replication source by hostid
        """
        response, code = get_sourcerep(kwargs['hostid'])
        return (response, code)

    @ddoc
    @doc(params={'hostid':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'host1',
                  'name': 'hostid',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete replication source
        """
        response, code = delete_sourcerep(kwargs['hostid'])
        return (response, code)

replication_sourcerep_view_func = SourcerepResource.as_view('sourcerep')
replication_sourereps_view_func = SourcerepsResource.as_view('sourcereps')

replication_api.add_url_rule(
    'sourcereps/<string:hostid>',
    view_func=replication_sourcerep_view_func,
    methods=['GET', 'DELETE'])

replication_api.add_url_rule(
    'sourcereps/',
    view_func=replication_sourereps_view_func,
    methods=['GET', 'POST'])
