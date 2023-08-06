import re
from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style, check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model)

from infiniguard_api.lib.hw.cli_handler import run_syscli1

log = iguard_logging.get_logger(__name__)


def create_storageserver(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        result, errmsg = run_syscli1(
            'add', 'storageserver', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='COMMAND FAILED')
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        # read back object just created
        cli_dict = dict(name=cli_dict['name'])
        return list_storageservers(cli_dict, None, http_code.CREATED, True)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)


def list_storageservers(cli_dict, request_values=None, response_code=None, verify_one=False):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        try:
            if request_values is None:
                request_values = {}
            per_page = int(request_values.get('page_size', '50'))
            page = int(request_values.get('page', '1'))
        except ValueError:
            error = build_error_model(
                error_message=['Wrong pagination parameters'],
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        result, errmsg = run_syscli1(
            'list', 'storageserver', parse_config_style, **cli_dict)
        if not isinstance(result, list):
            if 'E4001627' in errmsg:
                error = build_error_model(
                    error_message='Storage Server not found',
                    error_code='NOT_FOUND')
                return (build_entity_response(error=error), http_code.NOT_FOUND)
            else:
                error = build_error_model(
                    error_message=[errmsg],
                    error_code='COMMAND FAILED')
                return (build_entity_response(error=error), http_code.BAD_REQUEST)

        if verify_one == True:
            if len(result) != 1:
                error = build_error_model(
                    error_message=['Return more than one entry'],
                    error_code='WRONG_RETURN_VALUES',)
                return (build_entity_response(error=error), http_code.BAD_REQUEST)
            result = result[0]
            metadata = {'number_of_objects': 1}
        else:
            pagination = Pagination(per_page, page, 0)
            metadata = {
                'page_size': per_page,
                'page': pagination.page,
                'pages_total': pagination.pages,
                'number_of_objects': len(result)
            }

        response = dict(result=result, metadata=metadata)
        if response_code == None:
            response_code = http_code.OK
        return (response, response_code)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)


def get_storageserver(name):
    cli_dict = dict(name=name)
    return list_storageservers(cli_dict, None, http_code.OK, True)


def update_storageserver(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        storageserver_name = cli_dict.get('name', None)
        cli_dict['name'] = storageserver_name

        result, errmsg = run_syscli1(
            'edit', 'storageserver', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='COMMAND FAILED')
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        # read back object just created
        cli_dict = dict(name=cli_dict['name'])
        return list_storageservers(cli_dict, None, http_code.OK, True)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)


def delete_storageserver(name):
    try:
        cli_dict = {'name': name}
        result, errmsg = run_syscli1(
            'del', 'storageserver', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='COMMAND FAILED')
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

        data = dict(message=messages.DELETE_SUCCESS_MSG.format(name))
        return (data, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)
