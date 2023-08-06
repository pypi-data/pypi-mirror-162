from flask_apispec import use_kwargs, marshal_with, doc, MethodResource
from flask import Blueprint, request

from infiniguard_api.model.user_schemas import UserSchema, UserEditSchema, UsersPaginatedSchema, UserNonPaginatedSchema, USER_ROLES
from infiniguard_api.model.base_schema import PaginatedResponseSchema, ErrorResponseSchema, DeleteMessageSchema
from infiniguard_api.controller.user import list_users, list_user, create_user, update_user, delete_user
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc

user_api = Blueprint('user_api', __name__)


@ddoc
class UsersResource(MethodResource):
    """
    :Methods: GET, POST
    :Tags: Users
    """
    @ddoc
    @doc(operationId='list_users')
    @doc(params={'name':
                 {'in': 'query',
                  'description': 'User name',
                  'type': 'string',
                  'required': False},
                 'role':
                 {'in': 'query',
                  'description': 'User role',
                  'type': 'string',
                  'required': False,
                  'enum': USER_ROLES},
                 'page_size':
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
    @marshal_with(UsersPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self):
        """
        :Summary: List users by name
        """
        response, code = list_users(request.values)
        return (response, code)

    @ddoc
    @doc(operationId='create_user')
    @use_kwargs(UserSchema)
    @marshal_with(UserNonPaginatedSchema, code=http_code.CREATED)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create user
        """
        response, code = create_user(kwargs)
        return (response, code)


@ddoc
class UserResource(MethodResource):
    """
    :Methods: GET, PATCH, DELETE
    :Tags: Users
    """
    @ddoc
    @doc(operationId='list_user')
    @doc(params={'page_size':
                 {'in': 'query',
                  'description': 'Requested amount of items per page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False},
                 'role':
                 {'in': 'query',
                  'description': 'User role',
                  'type': 'string',
                  'required': True,
                  'enum': USER_ROLES},
                 'page':
                 {'in': 'query',
                  'description': 'Requested output page',
                  'type': 'integer',
                  'minimum': 1,
                  'required': False}})
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'username',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(UserNonPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: List users by role
        """
        response, code = list_user(kwargs['name'], request.values)
        return (response, code)

    @ddoc
    @doc(operationId='update_user')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'username',
                  'name': 'name',
                  'required': True}
                 })
    @use_kwargs(UserEditSchema(exclude=['name']))
    @marshal_with(UserNonPaginatedSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    @doc(params={'role':
                 {'in': 'query',
                  'description': 'User role',
                  'type': 'string',
                  'required': True,
                  'enum': USER_ROLES},
                 })
    def patch(self, **kwargs):
        """
        :Summary: Update user
        """
        response, code = update_user(kwargs, request.values)
        return (response, code)

    @ddoc
    @doc(operationId='delete_user')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'username',
                  'name': 'name',
                  'required': True}
                 })
    @marshal_with(DeleteMessageSchema, code=http_code.OK)
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    @doc(params={'role':
                 {'in': 'query',
                  'description': 'User role',
                  'type': 'string',
                  'required': True,
                  'enum': USER_ROLES},
                 })
    def delete(self, **kwargs):
        """
        :Summary: Delete user
        """
        response, code = delete_user(kwargs['name'], request.values)
        return (response, code)


user_view_func = UserResource.as_view('user')
users_view_func = UsersResource.as_view('users')

user_api.add_url_rule(
    '/',
    view_func=users_view_func,
    methods=['GET', 'POST'])
user_api.add_url_rule(
    '/<string:name>',
    view_func=user_view_func,
    methods=['GET', 'PATCH', 'DELETE'])
