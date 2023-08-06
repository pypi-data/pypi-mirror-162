from flask_apispec import (use_kwargs, marshal_with,
                                                                 doc, MethodResource)

from infiniguard_api.model.base_schema import ErrorResponseSchema, DeleteMessageSchema

from infiniguard_api.model.nas_schemas import (NasShareCreateSchema,
                                               NasShareEditSchema,
                                               AppSpecificSharesPaginatedSchema,
                                               AppSpecificSharePaginatedSchema)
from infiniguard_api.model.task_schemas import (TaskSchema)

from infiniguard_api.controller.nas.share import (create_share,
                                                  list_shares,
                                                  update_share,
                                                  delete_shares,
                                                  delete_share,
                                                  get_share,
                                                  list_share)

from flask import request

from infiniguard_api.view.nas import nas_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc


@ddoc
class AppSpecificSharesResource(MethodResource):
    """
    :Methods: GET, POST, DELETE
    :Tags: NAS App Specific Shares
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
    @marshal_with(AppSpecificSharesPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List APP_SPECIFIC shares
        """
        kwargs['proto'] = 'app_specific'
        response, code = list_shares(kwargs, request.values)
        return (response, code)

    @ddoc
    @use_kwargs(NasShareCreateSchema(exclude=['protocol']))
    @marshal_with(AppSpecificSharePaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create APP_SPECIFIC share
        """
        kwargs['proto'] = 'app_specific'
        response, code = create_share(kwargs)
        return (response, code)

    @ddoc
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete all APP_SPECIFIC shares
        """
        cli_dict = {'proto': 'app_specific'}
        response, code = delete_shares(cli_dict)
        return (response, code)


@ddoc
class AppSpecificShareResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: NAS App Specific Shares
    """
    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(AppSpecificSharePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Get APP_SPECIFIC share by name
        """
        response, code = get_share(kwargs['name'])
        return (response, code)

    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @use_kwargs(NasShareEditSchema)
    @marshal_with(AppSpecificSharePaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Edit APP_SPECIFIC share
        """
        response, code = update_share(kwargs)
        return (response, code)

    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete APP_SPECIFIC share by name
        """
        response, code = delete_share(kwargs['name'])
        return (response, code)


@ddoc
class AppSpecificShareFilesResource(MethodResource):
    """
    :Methods: POST
    :Tags: NAS App Specific Shares
    """
    @ddoc
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'share1',
                  'name': 'name',
                  'required': True}
                 })
    @doc(params={'mtime':
                 {'in': 'query',
                  'description': 'File age, in format lte:timestamp',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 })
    @marshal_with(TaskSchema, code=http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: List app specific share files
        :Description: List files on app specific share
        """
        response, code = list_share(kwargs, request.values)
        return response, code


app_specific_share_view_func = AppSpecificShareResource.as_view(
    'app_specific_share')
app_specific_shares_view_func = AppSpecificSharesResource.as_view(
    'app_specific_shares')
app_specific_share_files_view_func = AppSpecificShareFilesResource.as_view(
    'app_specific_share_files')

nas_api.add_url_rule(
    'app_specific/shares/<string:name>',
    view_func=app_specific_share_view_func,
    methods=['GET', 'PATCH', 'DELETE'])

nas_api.add_url_rule(
    'app_specific/shares/<string:name>/list_files',
    view_func=app_specific_share_files_view_func,
    methods=['POST'])

nas_api.add_url_rule(
    'app_specific/shares/',
    view_func=app_specific_shares_view_func,
    methods=['GET', 'POST', 'DELETE'])
