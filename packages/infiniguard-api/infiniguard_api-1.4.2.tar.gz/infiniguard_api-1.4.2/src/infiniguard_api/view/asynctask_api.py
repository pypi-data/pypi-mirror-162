from flask_apispec import (use_kwargs, marshal_with,
                           doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.asynctask_schemas import (AsynctasksPaginatedSchema,
                                                     AsynctaskPaginatedSchema,
                                                     AsynctaskDeleteMessageSchema,
                                                     AsynctaskListFilesResultsSchema,
                                                     AsynctaskListProgressResultsSchema)

from infiniguard_api.controller.asynctask import (list_asynctasks,
                                                  get_asynctask,
                                                  delete_asynctask,
                                                  get_asynctask_files,
                                                  get_asynctask_progress)

from flask import Blueprint, request

from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

asynctask_api = Blueprint('asynctask_api', __name__)


@ddoc
class AsynctasksResource(MethodResource):
    """
    :Methods: GET
    :Tags: Asynctasks
    """
    @ddoc
    @doc(operationId='list_asynctasks')
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
    @marshal_with(AsynctasksPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Returns all asynctasks
        """
        response, code = list_asynctasks(kwargs, request.values)
        return (response, code)


@ddoc
class AsynctaskResource(MethodResource):
    """
    :Methods: GET, DELETE
    :Tags: Asynctasks
    """
    @ddoc
    @doc(operationId='get_asynctask')
    @doc(params={'task_id':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '1572992039781',
                  'name': 'task_id',
                  'required': True}
                 })
    @marshal_with(AsynctaskPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return asynctask by task_id
        """
        response, code = get_asynctask(kwargs['task_id'])
        return (response, code)

    @ddoc
    @doc(operationId='delete_asynctask')
    @doc(params={'task_id':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '1572992039781',
                  'name': 'task_id',
                  'required': True}
                 })
    @marshal_with(AsynctaskDeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete task by task_id
        """
        response, code = delete_asynctask(kwargs['task_id'])
        return (response, code)


@ddoc
class AsynctaskFilesResource(MethodResource):
    """
    :Methods: GET
    :Tags: Asynctasks
    """
    @ddoc
    @doc(operationId='get_asynctask_files')
    @doc(params={'task_id':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '1572992039781',
                  'name': 'task_id',
                  'required': True}
                 })
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
    @marshal_with(AsynctaskListFilesResultsSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return asynctask file list
        """
        response, code = get_asynctask_files(kwargs, request.values)
        return (response, code)


@ddoc
class AsynctaskProgressResource(MethodResource):
    """
    :Methods: GET
    :Tags: Asynctasks
    """
    @ddoc
    @doc(operationId='get_asynctask_progress')
    @doc(params={'task_id':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': '1572992039781',
                  'name': 'task_id',
                  'required': True}
                 })
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
    @marshal_with(AsynctaskListProgressResultsSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return asynctask line list
        """
        response, code = get_asynctask_progress(kwargs, request.values)
        return (response, code)


asynctask_view_func = AsynctaskResource.as_view('asynctask')
asynctasks_view_func = AsynctasksResource.as_view('asynctasks')
asynctask_files_view_func = AsynctaskFilesResource.as_view('asynctask_files')
asynctask_progress_view_func = AsynctaskProgressResource.as_view(
    'asynctask_progress')


asynctask_api.add_url_rule(
    '/<string:task_id>',
    view_func=asynctask_view_func,
    methods=['GET', 'DELETE'])

asynctask_api.add_url_rule(
    '/',
    view_func=asynctasks_view_func,
    methods=['GET'])

asynctask_api.add_url_rule(
    '/<string:task_id>/file_results',
    view_func=asynctask_files_view_func,
    methods=['GET'])

asynctask_api.add_url_rule(
    '/<string:task_id>/progress_results',
    view_func=asynctask_progress_view_func,
    methods=['GET'])
