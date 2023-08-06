from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style_raw, check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model)

from infiniguard_api.lib.hw.cli_handler import run_syscli1

log = iguard_logging.get_logger(__name__)

SMBSETTING_OPTIONS = ['serversigning', 'oplocks']

def get_smbsetting(cli_dict, option):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)
        cli_args = []
        if option in SMBSETTING_OPTIONS:
            cli_args.append(option)
        else:
            error = build_error_model(
                error_message=["option choices: {}".format(SMBSETTING_OPTIONS)],
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)
        result, errmsg = run_syscli1('get', 'smbsetting', parse_config_style_raw, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)
        metadata = {'number_of_objects': 1}
        response = dict(result=result[0], metadata=metadata)
        return (response, http_code.OK)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def set_smbsetting(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        if cli_dict.get('serversigning', None):
            option = 'serversigning'
        else:
            option = 'oplocks'
        result, errmsg = run_syscli1('set', 'smbsetting', check_command_successful, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        #read back smbsetting
        cli_dict = {}
        return get_smbsetting(cli_dict, option)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)
