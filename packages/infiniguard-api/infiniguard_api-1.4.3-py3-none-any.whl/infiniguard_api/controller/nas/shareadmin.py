from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style, parse_config_style_raw, check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model)

from infiniguard_api.lib.hw.cli_handler import run_syscli1

log = iguard_logging.get_logger(__name__)

def create_shareadmin(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        result, errmsg = run_syscli1('add', 'shareadmin', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        #read back object just created
        cli_dict = dict(name=cli_dict['name'])
        return list_shareadmins(cli_dict, None, http_code.CREATED, True)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def list_shareadmins(cli_dict, request_values=None, response_code=None, verify_one=False):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        try:
            if request_values is None:
                request_values = {}
            per_page = int(request_values.get('page_size', '50'))
            page = int(request_values.get('page', '1'))
        except ValueError:
            error = build_error_model(
                error_message=['Wrong pagination parameters'],
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        name = cli_dict.pop('name', None)
        parse_func = parse_config_style
        result, errmsg = run_syscli1('list', 'shareadmin', parse_func, **cli_dict)
        if not isinstance(result, list):
            if not result:
                error = build_error_model(
                    error_message=[errmsg],
                    error_code='COMMAND FAILED')
                return (build_entity_response(error=error), 400)

        if verify_one == True:
            metadata = {'number_of_objects': 0}
            for entry in result:
                if entry.get('name', None) == name:
                    result = entry
                    metadata['number_of_objects'] = 1
                    break
            if metadata['number_of_objects'] == 0:
                error = build_error_model(
                    error_message=['Item not found'],
                    error_code='COMMAND FAILED')
                return (build_entity_response(error=error), 401)
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
        return (build_entity_response(error=error), 400)

def get_shareadmin(cli_dict):
    return list_shareadmins(cli_dict, None, http_code.OK, True)

def delete_shareadmin(cli_dict):
    try:
        result, errmsg = run_syscli1('del', 'shareadmin', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        data = dict(message=messages.DELETE_SUCCESS_MSG.format(cli_dict.get('name', None)))
        return (data, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def delete_shareadmins(cli_dict):
    try:
        cli_args = ['sure']
        result, errmsg = run_syscli1('deleteall', 'shareadmin', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)
        output = 'all shareadmin users'
        data = dict(message=messages.DELETE_SUCCESS_MSG.format(output))
        return (data, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)