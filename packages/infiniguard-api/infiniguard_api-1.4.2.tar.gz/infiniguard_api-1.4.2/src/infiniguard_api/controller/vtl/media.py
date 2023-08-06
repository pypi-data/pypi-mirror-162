import re
from datetime import datetime, timedelta
from time import sleep

from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style, check_command_successful, parse_async

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model,
                                             build_async_task_response)

from infiniguard_api.controller.vtl.partition import (get_partition)
from infiniguard_api.controller.vtl.drive import (list_drives,
                                                  list_mediatypes)

from infiniguard_api.lib.hw.cli_handler import run_syscli1

log = iguard_logging.get_logger(__name__)

def create_media(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        partition_name = cli_dict.get('name', None)
        cli_dict['name'] = partition_name

        #figure out default media type
        if not cli_dict.get('type', None):
            response, code = get_partition(partition_name)
            if code != http_code.OK:
                return (response, code)
            drivemodel = response['result']['drivemodel']

            kwargs = dict()
            response, code = list_drives(kwargs, None)
            if code != http_code.OK:
                return (response, code)
            drives = response['result']
            drivetype = None
            for drive in drives:
                if drivemodel == drive['description']:
                    drivetype = drive['modelnumber']
                    break
            if drivetype == None:
                error = build_error_model(
                error_message=["drive type {} not found".format(drivemodel)],
                error_code='COMMAND FAILED')
                return (build_entity_response(error=error), 400)

            kwargs = dict(drivetype=drivetype)
            response, code = list_mediatypes(kwargs, None)
            if code != http_code.OK:
                return (response, code)
            response['result'].sort(key=lambda x: x.get('type', None), reverse=True)
            mediatype = response['result'][0]['type']
            cli_dict['type'] = mediatype
        parser = check_command_successful
        is_async = cli_dict.pop('asyncronous', False)
        if is_async:
            parser = parse_async
        result, errmsg = run_syscli1('add', 'media', parser, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        if parser == parse_async:
            task_id = result
            response = build_async_task_response(task_id)
            return response, http_code.ACCEPTED

        #read back object just created
        new_cli_dict = dict(name=cli_dict['name'], barcode=cli_dict['barcodestart'], media=cli_dict['media'])
        return list_media(new_cli_dict, None, http_code.CREATED, True)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def list_media(cli_dict, request_values=None, response_code=None, verify_one=False):
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

        cli_args = []
        media = cli_dict.pop('media', 0)
        barcode = cli_dict.pop('barcode', None)
        verify_one = False
        if media == 0:
            if not barcode:
                cli_args.append('all')
            else:
                verify_one = True
                cli_dict['barcode'] = barcode
        else:
            cli_args.append('all')

        result, errmsg = run_syscli1('list', 'media', parse_config_style, *cli_args, **cli_dict)
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
            if media != 0:
                start_barcode = int(re.search('\d+$', barcode).group())
                end_barcode = int(start_barcode + media)
                for entry in result:
                    entry_barcode = int(re.search('\d+$', entry['barcode']).group())
                    if entry_barcode < start_barcode or entry_barcode >= end_barcode:
                        result.remove(entry)
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

def delete_all_media(cli_dict):
    try:
        cli_args = ['sure']
        result, errmsg = run_syscli1('deleteall', 'media', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)
        output = 'all media for VTL partition {}'.format(cli_dict.get('name', None))
        data = dict(message=messages.DELETE_SUCCESS_MSG.format(output))
        return (data, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def get_media(partition, barcode):
    cli_dict = dict(barcode=barcode, name=partition)
    return list_media(cli_dict, None, http_code.OK, True)

def delete_media(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        result, errmsg = run_syscli1('del', 'media', check_command_successful, **cli_dict)
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

def import_media(name, barcode):
    try:
        cli_dict = dict(name=name)
        if not barcode:
            cli_args = ['all']
        else:
            cli_args = []
            cli_dict['barcode'] = barcode
        result, errmsg = run_syscli1('import', 'media', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def export_media(name, barcode):
    try:
        cli_dict = dict(name=name)
        if not barcode:
            cli_args = ['all']
        else:
            cli_args = []
            cli_dict['barcode'] = barcode
        result, errmsg = run_syscli1('export', 'media', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def recycle_media(name, barcode):
    try:
        cli_dict = dict(name=name)
        if not barcode:
            cli_args = ['all']
        else:
            cli_args = []
            cli_dict['barcode'] = barcode
        result, errmsg = run_syscli1('recycle', 'media', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def unload_media(cli_dict):
    try:
        name = cli_dict.get('name', None)
        barcode = cli_dict.get('barcode', None)
        cli_dict['name'] = name
        cli_dict['barcode'] = barcode
        cli_args = []
        forceunload = cli_dict.pop('forceunload', False)
        if forceunload:
            cli_args = ['forceunload']
        result, errmsg = run_syscli1('unload', 'media', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def write_protect_media(name, barcode, disable):
    try:
        cli_dict = dict(name=name)
        if not barcode:
            cli_args = ['all']
        else:
            cli_args = []
            cli_dict['barcode'] = barcode
        if disable == True:
            cli_args.append('disable')
        result, errmsg = run_syscli1('writeprot', 'media', check_command_successful, *cli_args, **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, http_code.OK)
    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)

def move_media(cli_dict):
    try:
        if cli_dict.get('errors', None):
            error = build_error_model(
                error_message=build_error_message(cli_dict['errors']),
                error_code='WRONG_FIELD_VALUES',)
            return (build_entity_response(error=error), 400)

        partition_name = cli_dict.get('name', None)
        cli_dict['name'] = partition_name
        cli_args = []
        forceunload = cli_dict.pop('forceunload', False)
        if forceunload:
            cli_args = ['forceunload']
        result, errmsg = run_syscli1('move', 'media', check_command_successful, *cli_args,  **cli_dict)
        if not result:
            error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
            return (build_entity_response(error=error), 400)

        return (None, http_code.OK)

    except Exception as e:
        error = build_error_model(
            error_message=[e.message],
            error_code='UNEXPECTED_EXCEPTION')
        return (build_entity_response(error=error), 400)
