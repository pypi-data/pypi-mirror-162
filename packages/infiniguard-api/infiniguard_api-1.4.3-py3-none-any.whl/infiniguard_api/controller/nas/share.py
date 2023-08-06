from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style, parse_config_style_raw, check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model,
                                             error_handler,
                                             build_async_task_response)

from infiniguard_api.lib.hw.cli_handler import run_syscli1, run_python
from infiniguard_api.lib.iguard_api_exceptions import IguardApiFieldException, IguardApiQueryException, IguardApiFilterException

import os
import sys
import json
from time import ctime, mktime, gmtime, asctime

log = iguard_logging.get_logger(__name__)


def get_prefix():
    return '/snfs/ddup/shares/'


@error_handler
def create_share(cli_dict):
    cli_args = []
    permissions = cli_dict.pop('permissions', 'rw')
    if permissions == 'ro':
        cli_args.append('ro')

    dedup = cli_dict.pop('dedup', False)
    if dedup:
        cli_args.append('dedup')

    proto = cli_dict.pop('protocol', None)
    if not cli_dict.get('proto', None):
        cli_dict['proto'] = proto

    hidden = cli_dict.pop('hidden', False)
    if proto == 'cifs' and hidden:
        cli_args.append('hidden')

    result, errmsg = run_syscli1(
        'add', 'share', check_command_successful, *cli_args, **cli_dict)
    if not result:
        error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    # read back object just created
    cli_dict = dict(name=cli_dict['name'])
    return list_shares(cli_dict, None, http_code.CREATED, True)


@error_handler
def list_shares(cli_dict, request_values=None, response_code=None, verify_one=False):
    def get_access(entry):
        if 'Allowed' in entry:
            return 'Allowed'
        else:
            return 'All'
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

    parse_func = parse_config_style_raw if verify_one == True else parse_config_style
    result, errmsg = run_syscli1('list', 'share', parse_func, **cli_dict)
    if not isinstance(result, list):
        if 'E1002921' in errmsg:
            error = build_error_model(
                error_message='Share not found',
                error_code='NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)
        else:
            error = build_error_model(
                error_message=[errmsg],
                error_code='COMMAND FAILED')
            return (build_entity_response(error=error), http_code.BAD_REQUEST)

    for entry in result:
        if not entry.get('protocol', None) == 'cifs':
            entry.pop('hidden', False)
        access = entry.get('access', None)
        if access:
            access_list = access.split(',')
            for item in access_list:
                if 'users' in item:
                    entry['access_users'] = get_access(item)
                elif 'hosts' in item:
                    entry['access_hosts'] = get_access(item)

    if verify_one is True:
        if len(result) != 1:
            error = build_error_model(
                error_message=['Return more than one entry'],
                error_code='WRONG_RETURN_VALUES',)
            return (build_entity_response(error=error), http_code.BAD_REQUEST)
        result = result[0]
        metadata = {}
    else:
        pagination = Pagination(per_page, page, len(result))
        metadata = {
            'page_size': per_page,
            'page': pagination.page,
            'pages_total': pagination.pages,
            'number_of_objects': len(result)
        }
        result = result[pagination.offset:pagination.offset + per_page]

    response = dict(result=result, metadata=metadata)
    if response_code is None:
        response_code = http_code.OK
    return (response, response_code)


def get_share(name):
    cli_dict = dict(name=name)
    return list_shares(cli_dict, None, http_code.OK, True)


@error_handler
def update_share(cli_dict):
    storageserver_name = cli_dict.get('name')
    cli_dict['name'] = storageserver_name

    result, errmsg = run_syscli1(
        'edit', 'share', check_command_successful, **cli_dict)
    if not result:
        error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    # read back object just created
    cli_dict = dict(name=cli_dict['name'])
    return list_shares(cli_dict, None, http_code.OK, True)


@error_handler
def delete_share(name):
    cli_dict = {'name': name}
    result, errmsg = run_syscli1(
        'del', 'share', check_command_successful, **cli_dict)
    if not result:
        error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    data = dict(message=messages.DELETE_SUCCESS_MSG.format(name))
    return (data, http_code.OK)


@error_handler
def delete_shares(cli_dict):
    cli_args = ['sure']
    result, errmsg = run_syscli1(
        'deleteall', 'share', check_command_successful, *cli_args, **cli_dict)
    if not result:
        error = build_error_model(
            error_message=[errmsg],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)
    output = '{} shares'.format(cli_dict.get('proto', 'all'))
    data = dict(message=messages.DELETE_SUCCESS_MSG.format(output))
    return (data, http_code.OK)


def do_list_share(params):
    location = params.get('location') 
    since = params.get('since')
    try:
        files_in_dir = []
        loclen = len(location) + 1
        # r=>root, d=>directories, f=>files
        for r, d, f in os.walk(location):
            for item in f:
                path = os.path.join(r, item)
                try:
                    realpath = os.path.realpath(path)
                    stat = os.stat(path)
                    size = stat.st_size
                    ctime = int(stat.st_ctime)
                    mtime = int(stat.st_mtime)
                    mode = stat.st_mode
                    uid = stat.st_uid
                    gid = stat.st_gid
                except Exception:
                    size = 0
                    ctime = 0
                    mtime = 0
                    mode = 0
                    uid = 0
                    gid = 0
                if mtime < since:
                    yield (0, (path[loclen:], size, ctime, mtime, mode, uid, gid), "")
    except Exception as e:
        yield (1, "", repr(e))


@error_handler
def list_share(cli_dict, request_values):
    share_name = cli_dict.get('name', None)
    prefix = get_prefix()
    relative_path = '{}{}'.format(prefix, share_name)
    abs_path = os.path.abspath(relative_path)

    if not abs_path.startswith(prefix) or not os.path.isdir(abs_path):
        error = build_error_model(
            error_message=['Share {} not found'.format(share_name)],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.NOT_FOUND)

    valid_fields = ['mtime']
    ignore_fields = ['approved']
    since = 4294967295  # Very large number in the future - Sunday, 7 February 2106
    try:
        if request_values is None:
            request_values = {}
        for k, v in request_values.items():
            if k in ignore_fields:
                continue
            if k not in valid_fields:
                raise IguardApiQueryException(k)
            v_filter = v.split(":")[0]
            if v_filter not in ["lte"]:
                raise IguardApiFilterException(v_filter)
            v_value = v.split(":")[-1]
            since = int(v_value)

    except IguardApiQueryException as e:
        error = build_error_model(
            error_message=['Wrong query parameter {}'.format(e)],
            error_code='ATTRIBUTE_NOT_FOUND',)
        return (build_entity_response(error=error), http_code.BAD_REQUEST)
    except IguardApiFilterException as e:
        error = build_error_model(
            error_message=['Wrong filter parameter {}'.format(e)],
            error_code='UNSUPPORTED_FIELD',)
        return (build_entity_response(error=error), http_code.BAD_REQUEST)
    except ValueError:
        error = build_error_model(
            error_message=['Wrong timestamp format'],
            error_code='WRONG_FIELD_VALUES',)
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    parameters = {
        'location': prefix + share_name,
        'since': since
    }
    result = run_python(parameters, do_list_share, 'do_list_share')
    if not result:
        error = build_error_model(
            error_message=['Failed to run list_share'],
            error_code='COMMAND FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    task_id = result
    response = build_async_task_response(task_id)
    return response, http_code.ACCEPTED
