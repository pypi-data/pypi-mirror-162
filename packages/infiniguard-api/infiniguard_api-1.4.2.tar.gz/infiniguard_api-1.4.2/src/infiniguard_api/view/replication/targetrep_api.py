from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.replication_schemas import (ReplicationTargetCreateSchema,
                                                       ReplicationTargetsPaginatedSchema,
                                                       ReplicationTargetPaginatedSchema)

from infiniguard_api.controller.replication.targetrep import (create_targetrep,
                                                              list_targetreps,
                                                              delete_targetrep,
                                                              pause_targetrep,
                                                              resume_targetrep,
                                                              get_targetrep)

from flask import request

from infiniguard_api.view.replication import replication_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

@ddoc
class TargetrepsResource(MethodResource):
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
    @marshal_with(ReplicationTargetsPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns the configuration for all replication targets
        """
        response, code = list_targetreps(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(ReplicationTargetCreateSchema)
    @marshal_with(ReplicationTargetPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create replication target
        """
        response, code = create_targetrep(kwargs)
        return (response, code)

@ddoc
class TargetrepResource(MethodResource):
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
    @marshal_with(ReplicationTargetPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return replication target by hostid
        """
        response, code = get_targetrep(kwargs['hostid'])
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
        :Summary: Delete replication target
        """
        response, code = delete_targetrep(kwargs['hostid'])
        return (response, code)

    @ddoc
    @doc(params={'hostid':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'host1',
                  'name': 'hostid',
                  'required': True}
                 })
    @marshal_with(MessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Pause/resume replication target
        """
        hostid = kwargs['hostid']
        path = request.path
        operation = path.split('/')[-1]
        if operation == 'pause':
            response, code = pause_targetrep(hostid)
        elif operation == 'resume':
            response, code = resume_targetrep(hostid)
        return (response, code)

replication_targetrep_view_func = TargetrepResource.as_view('targetrep')
replication_targetreps_view_func = TargetrepsResource.as_view('targetreps')

replication_api.add_url_rule(
    'targetreps/<string:hostid>',
    view_func=replication_targetrep_view_func,
    methods=['GET', 'DELETE'])

replication_api.add_url_rule(
    'targetreps/<string:hostid>/pause',
    view_func=replication_targetrep_view_func,
    methods=['POST'])

replication_api.add_url_rule(
    'targetreps/<string:hostid>/resume',
    view_func=replication_targetrep_view_func,
    methods=['POST'])

replication_api.add_url_rule(
    'targetreps/',
    view_func=replication_targetreps_view_func,
    methods=['GET', 'POST'])
