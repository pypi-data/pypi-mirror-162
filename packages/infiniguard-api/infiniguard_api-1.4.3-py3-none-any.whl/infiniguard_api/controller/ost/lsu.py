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

def create_lsu(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        storageserver_name = cli_dict.get('storageserver', None)
        cli_dict['storageserver'] = storageserver_name
        cli_args = []
        capacity = cli_dict.pop('capacity', 0)
        unlimited = True if capacity == 0 else False
        if unlimited:
            cli_args.append('unlimited')
        else:
            cli_dict['capacity'] = capacity

        result, errmsg = run_syscli1('add', 'lsu', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)


        #read back object just created
        new_cli_dict = dict(storageserver=cli_dict['storageserver'])
        if cli_args != ['unlimited']:
            new_cli_dict['name'] = cli_dict['name']
        return list_lsus(new_cli_dict, None, http_code.CREATED, True)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def list_lsus(cli_dict, request_values=None, response_code=None, verify_one=False):
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

        result, errmsg = run_syscli1('list', 'lsu', parse_config_style, **cli_dict)
        if not isinstance(result, list):
            if not result:
                error = build_error_model(
                    error_message=[errmsg],
                    error_code='COMMAND FAILED')
                return (build_entity_response(error=error), 400)

        if verify_one == True:
            if len(result) != 1:
                error = build_error_model(
                error_message=['Return more than one entry'],
                error_code='WRONG_RETURN_VALUES',)
                return (build_entity_response(error=error), 400)
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
        return (build_entity_response(error=error), 400)

def get_lsu(storageserver, name):
    cli_dict = dict(name=name, storageserver=storageserver)
    return list_lsus(cli_dict, None, http_code.OK, True)

def update_lsu(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        lsu_name = cli_dict.get('name', None)
        storageserver_name = cli_dict.get('storageserver', None)
        cli_dict['name'] = lsu_name
        cli_dict['storageserver'] = storageserver_name

        result, errmsg = run_syscli1('edit', 'lsu', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        #read back object just created
        cli_dict = dict(storageserver=cli_dict['storageserver'], name=cli_dict['name'])
        return list_lsus(cli_dict, None, http_code.OK, True)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def delete_lsu(cli_dict, force='FALSE'):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        cli_args = []
        if force == 'TRUE':
            force = True
        elif force == 'FALSE':
            force = False
        else:
            error = build_error_model(
                error_message=["force: Not a valid choice."],
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        if force:
            cli_args.append('force')
        result, errmsg = run_syscli1('del', 'lsu', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)
        name = cli_dict['name']
        data = dict(message=messages.DELETE_SUCCESS_MSG.format(name))
        return (data, http_code.OK)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

