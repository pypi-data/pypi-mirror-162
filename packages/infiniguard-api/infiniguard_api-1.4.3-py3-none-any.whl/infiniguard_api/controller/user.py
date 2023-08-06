from schematics.exceptions import DataError
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.common import messages

from infiniguard_api.lib.hw.output_parser import (parse_list_user,
                                                  check_command_successful, parse_async)
from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model)

from infiniguard_api.lib.rest.pagination import Pagination
from infiniguard_api.model.models import UserModel, USER_ROLES

from infiniguard_api.lib.hw.cli_handler import (run_syscli,
                                                run_syscli1,
                                                create_user_command,
                                                delete_user_command,
                                                update_user_command,
                                                list_users_command
                                                )

from infiniguard_api.lib.hw.cmd_spec import create_syscli_command
from infiniguard_api.lib.rest.common import http_code

log = iguard_logging.get_logger(__name__)

def _get_users(role, username=None):
    try:
        command_line = list_users_command(role)
        res, err = run_syscli1(*command_line, parse_list_user)
        if err:
            return None, err

        results = list()
        for entry in res:
            _name = entry.pop('name', entry.get('username'))
            if not username or username == _name:
                entry['username'] = _name
                entry['role'] = role
                user = UserModel(entry, strict=False)
                user.validate()
                results.append(user.to_native())
        return results, None
    except DataError as e:
        return None, e.messages
    except Exception as e:
        return None, str(e)


def create_user(user_dict):
    if user_dict.get('errors', None):
        error = build_error_model(
            error_message=build_error_message(user_dict['errors']),
            error_code='WRONG_FIELD_VALUES')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    cli_args = []
    admin = user_dict.get('admin', False)
    if admin:
        cli_args.append('admin')

    try:
        user = UserModel.validated(**user_dict)
        if user.password is None:
            raise DataError({'create_user': "Password can't be empty"})
    except DataError as e:
        error = build_error_model(
            error_message=build_error_message(e.messages),
            error_code='WRONG_FIELD_VALUES')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    # here persist user
    command_line = create_user_command(username=user.name,
                                       role=user.role,
                                       password=user.password,
                                       description=user.description
                                       )
    result, err = run_syscli1(
        command_line[0],
        command_line[1],
        check_command_successful,
        *cli_args,
        **command_line[2]
    )
    if not result:
        error = build_error_model(
            error_message=[err],
            error_code='ERROR_CREATE_USER')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)
    res, err = _get_users(user.role, user.name)
    if not res:
        error = build_error_model(
            error_message=[err],
            error_code='ERROR_GET_USER')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)

    log.info(user=user)
    metadata = {'number_of_objects': 1}
    return (build_entity_response(
        metadata=metadata,
        result=res[0]), http_code.CREATED)





def list_users(request_args):
    name = request_args.get('name', None)
    user_role = request_args.get('role', None)
    if user_role and user_role not in USER_ROLES:
        error = build_error_model(
            error_message=["role choices: {}".format(USER_ROLES)],
            error_code='WRONG_FIELD_VALUES',)
        return (build_entity_response(error=error), http_code.BAD_REQUEST)
    try:
        per_page = int(request_args.get('page_size', '50'))
        page = int(request_args.get('page', '1'))
    except ValueError:
        error = build_error_model(
            error_message=['Wrong pagination parameters'],
            error_code='WRONG_FIELD_VALUES')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)

    result = list()
    for role in USER_ROLES:
        if not user_role or user_role == role:
            res, err = _get_users(role, name)
            if err:
                error = build_error_model(
                    error_message=[err],
                    error_code='ERROR_GET_USERS')
                return (build_paginated_response(error=error), http_code.BAD_REQUEST)
            result += res

    pagination = Pagination(per_page, page, len(result))
    metadata = {
        'page_size': pagination.page_size,
        'page': pagination.page,
        'pages_total': pagination.pages,
        'number_of_objects': pagination.number_of_objects
    }

    return (build_paginated_response(result=result,
                                     metadata=metadata), http_code.OK)


def list_user(name, request_args):
    try:
        per_page = int(request_args.get('page_size', '50'))
        page = int(request_args.get('page', '1'))
    except ValueError:
        error = build_error_model(
            error_message=['Wrong pagination parameters'],
            error_code='WRONG_FIELD_VALUES')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)
    role = request_args.get('role', USER_ROLES[0])

    result, err = _get_users(role, name)
    if err or not result:
        error = build_error_model(
            error_message=[err if err else 'User not found'],
            error_code='USER_NOT_FOUND')
        return (build_paginated_response(error=error), http_code.NOT_FOUND)
    return (build_entity_response(result=result[0]), http_code.OK)


def update_user(request_args, request_values):
    if request_args.get('errors', None):
        error = build_error_model(
            error_message=build_error_message(request_args['errors']),
            error_code='WRONG_FIELD_VALUES')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    try:
        user_dict = dict(request_args)
        user_dict['name'] = request_args['name']
        user_dict['role'] = request_values['role']
        if user_dict['role'] != 'workgroup' and user_dict.get('admin', None):
            raise DataError(
                {'update_user': 'Admin should be used for workgroup user only'})
        user = UserModel(user_dict, strict=False)
        user.validate()
        if user.password is None and user.description is None:
            raise DataError(
                {'update_user': 'Description and/or password should be updated'})
    except DataError as e:
        error = build_error_model(
            error_message=build_error_message(e.messages),
            error_code='ERROR_UPDATE_USER')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)

    cmd = update_user_command(username=user.name,
                              role=user.role,
                              password=user.password,
                              description=user.description,
                              admin=user.admin)
    result, err = run_syscli1(
        cmd[0],
        cmd[1],
        check_command_successful,
        **cmd[2]
    )
    if not result:
        error = build_error_model(
            error_message=[err],
            error_code='ERROR_UPDATE_USER')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)

    res, err = _get_users(user.role, user.name)
    if not res:
        error = build_error_model(
            error_message=[err],
            error_code='ERROR_GET_USER')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)
    return (build_entity_response(result=res[0]), http_code.OK)


def delete_user(username, request_args):
    role = request_args.get('role', USER_ROLES[0])
    cmd = delete_user_command(username=username,
                              role=role,
                              )
    result, err = run_syscli1(
        cmd[0],
        cmd[1],
        check_command_successful,
        **cmd[2]
    )
    if not result:
        error = build_error_model(
            error_message=[err],
            error_code='ERROR_DELETE_USER')
        return (build_paginated_response(error=error), http_code.BAD_REQUEST)
    data = dict(message=messages.DELETE_SUCCESS_MSG.format(username))
    return (data, http_code.OK)
