from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.hw.output_parser import check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model)

from infiniguard_api.lib.hw.cli_handler import run_syscli1

log = iguard_logging.get_logger(__name__)

def join_adsdomain(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        result, errmsg = run_syscli1('join', 'ads', check_command_successful, **cli_dict)
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

def disjoin_adsdomain(cli_dict):
    try:
        result, errmsg = run_syscli1('disjoin', 'ads', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        data = dict(message=messages.DISJOIN_ADSDOMAIN_SUCCESS_MSG)
        return (data, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)