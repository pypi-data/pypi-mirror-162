from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style, check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model)

from infiniguard_api.lib.hw.cli_handler import run_syscli1

log = iguard_logging.get_logger(__name__)

def install_tlscertificate(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)
    
        result, errmsg = run_syscli1('install', 'tlscertificate', check_command_successful, 'sure', 'deferreboot', **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, 201)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def list_tlscertificates(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)
        try:
            per_page = int(cli_dict.get('page_size', '50'))
            page = int(cli_dict.get('page', '1'))
        except ValueError:
            error = build_error_model(
                error_message=['Wrong pagination parameters'],
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)
    
        pagination = Pagination(per_page, page, 0)
        metadata = {
            'page_size': per_page,
            'page': pagination.page,
            'pages_total': pagination.pages,
            'number_of_objects': pagination.number_of_objects
        }
        result, errmsg = run_syscli1('getstatus', 'tlscertificate', parse_config_style, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        metadata['number_of_objects'] = len(result)
        response = dict(result=result, metadata=metadata)
        return (response, 200)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def restore_tlscertificate():
    try:
        cli_dict = {}
        result, errmsg = run_syscli1('restore', 'tlscertificate', check_command_successful, 'sure', 'deferreboot', **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, 204)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

