import re
from infiniguard_api.lib.logging import iguard_logging

from infiniguard_api.lib.rest.common import http_code

from infiniguard_api.common import messages

from infiniguard_api.lib.rest.pagination import Pagination

from infiniguard_api.lib.hw.output_parser import parse_config_style, check_command_successful

from infiniguard_api.lib.rest.common import (build_error_message,
                                             build_paginated_response,
                                             build_entity_response,
                                             build_error_model,
                                             error_handler,
                                             validate_request_values)

from infiniguard_api.lib.hw.tasks import (get_tasks,
                                          get_task,
                                          delete_task,
                                          get_files,
                                          get_file_num,
                                          get_progress,
                                          get_progress_num
                                          )
from infiniguard_api.lib.iguard_api_exceptions import IguardApiFieldException, IguardApiQueryException

log = iguard_logging.get_logger(__name__)


@error_handler
def list_asynctasks(cli_dict, request_values=None, response_code=None, verify_one=False):
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

    task_id = cli_dict.get('task_id', None)
    if task_id:
        result, errmsg = get_task(task_id)
    else:
        result, errmsg = get_tasks()

    if not isinstance(result, list):
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='TASK_NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)

    tasks = []
    for task in result:
        entry = dict(task_id=task.task_id, rc=task.rc, status=task.status,
                     stdout=task.stdout, stderr=task.stderr, start=task.start,
                     end=task.end, duration=task.duration, name=task.name,
                     command=task.command)
        tasks.append(entry)

    result = tasks

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


@error_handler
@validate_request_values(['filename', 'size', 'ctime',
                          'mtime', 'mode', 'uid', 'gid', 'id'])
def get_asynctask_files(cli_dict, request_values=None):
    per_page = int(request_values.get('page_size', '50'))
    page = int(request_values.get('page', '1'))

    task_id = cli_dict.get('task_id', None)
    result, errmsg = get_task(task_id)

    if not isinstance(result, list):
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='TASK_NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)

    try:
        total = get_file_num(task_id, request_values)
        log.info("Total files: {}".format(total))
        pagination = Pagination(per_page, page, total)
        metadata = {
            'page_size': per_page,
            'page': pagination.page,
            'pages_total': pagination.pages,
            'number_of_objects': total
        }
        filenames = get_files(task_id, (pagination.page - 1)
                              * per_page, pagination.page * per_page, request_values)
    except Exception as e:
        error = build_error_model(
            error_message=[str(e)],
            error_code='COMMAND_FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    files = []
    for file in filenames:
        filename, size, ctime, mtime, mode, uid, gid, row_id = file
        entry = dict(filename=filename, size=size, ctime=ctime,
                     mtime=mtime, mode=mode, uid=uid, gid=gid, id=row_id)
        files.append(entry)

    result = files

    response = dict(result=result, metadata=metadata)
    return (response, http_code.OK)


@error_handler
@validate_request_values(['timestamp', 'id', 'stdstream'])
def get_asynctask_progress(cli_dict, request_values=None):
    per_page = int(request_values.get('page_size', '50'))
    page = int(request_values.get('page', '1'))

    task_id = cli_dict.get('task_id', None)
    result, errmsg = get_task(task_id)

    if not isinstance(result, list):
        if not result:
            error = build_error_model(
                error_message=[errmsg],
                error_code='TASK_NOT_FOUND')
            return (build_entity_response(error=error), http_code.NOT_FOUND)

    try:
        total = get_progress_num(task_id, request_values)
        log.info("Total lines: {}".format(total))
        pagination = Pagination(per_page, page, total)
        metadata = {
            'page_size': per_page,
            'page': pagination.page,
            'pages_total': pagination.pages,
            'number_of_objects': total
        }
        lines = get_progress(task_id, (pagination.page - 1)
                             * per_page, pagination.page * per_page, request_values)
    except Exception as e:
        error = build_error_model(
            error_message=[str(e)],
            error_code='COMMAND_FAILED')
        return (build_entity_response(error=error), http_code.BAD_REQUEST)

    result = list()
    for line in lines:
        _id, _line, _timestamp, _stdstream = line
        entry = dict(line=_line, id=_id, timestamp=_timestamp,
                     stdstream=_stdstream)
        result.append(entry)

    response = dict(result=result, metadata=metadata)
    return (response, http_code.OK)


def get_asynctask(task_id):
    cli_dict = dict(task_id=task_id)
    return list_asynctasks(cli_dict, None, http_code.OK, True)


@error_handler
def delete_asynctask(task_id):
    result, errmsg = delete_task(task_id)
    if not result:
        error = build_error_model(
            error_message=[errmsg],
            error_code='TASK_NOT_FOUND')
        return (build_entity_response(error=error), http_code.NOT_FOUND)

    data = {
        "metadata": {
            "code": "DELETED",
        },
        "result": {
            "message": "Delete  task {} succeeded".format(task_id)
        }
    }
    return (data, http_code.OK)
