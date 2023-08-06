from __future__ import annotations
from http import HTTPStatus
from typing import Optional, Callable

from schematics.exceptions import ValidationError
from infiniguard_api.model.models import (ListResponseModel,
                                          EntityResponseModel,
                                          EmptyResponseModel,
                                          ErrorModel)
from infiniguard_api.lib.logging import iguard_logging
from infiniguard_api.lib.iguard_api_exceptions import IguardApiFieldException, IguardApiQueryException
from flask import request
from functools import wraps
from infiniguard_api.common.const import HEADER_USER as _HEADER_USER


HEADER_USER = _HEADER_USER
if isinstance(HEADER_USER, bytes):
    HEADER_USER = HEADER_USER.decode()

log = iguard_logging.get_logger(__name__)


class HttpResp(int):
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return str(other) > str(self.value)

    def __gt__(self, other):
        return str(other) < str(self.value)


http_code = HTTPStatus


def build_error_message(error_dict):
    error_message = []
    for field_name, error_msgs in error_dict.items():
        if isinstance(error_msgs, list):
            error_message.append(': '.join([field_name,
                                            ' '.join(error_msgs)]))
        elif isinstance(error_msgs, dict):
            error_message.append(
                ': '.join([field_name,
                           ' '.join(
                               [el
                                for msg in error_msgs.values()
                                for el in msg])]))
        elif isinstance(error_msgs, ValidationError):
            error_message.append(
                ': '.join([field_name,
                           ' '.join(
                               [msg
                                for msg in error_msgs.to_primitive()])]))
        else:
            error_message.append(': '.join([field_name, str(error_msgs)]))
    return error_message


def build_paginated_response(metadata=None,
                             error=None,
                             result=None):
    response = ListResponseModel.validated(metadata=metadata,
                                           error=error)
    response.result = result
    # FIXME not validating ListType(PolyModelType)
    return response


def build_entity_response(metadata=None,
                          error=None,
                          result=None):
    return EntityResponseModel.validated(metadata=metadata,
                                         error=error,
                                         result=result).to_primitive()


def build_empty_response():
    return EmptyResponseModel.validated(result=True).to_primitive()


def build_error_model(error_message, error_code):
    if isinstance(error_message, list):
        error_message = ", ".join([str(a) for a in error_message])
    elif isinstance(error_message, dict):
        error_message = ", ".join(sorted(["{}: '{}'".format(k, " ,".join(
            [str(a) for a in v])) for k, v in error_message.items()]))
    return ErrorModel.validated(
        message=error_message,
        code=error_code)


def handle_error(err):
    exc = getattr(err, 'exc')
    if exc:
        message = exc.messages
    else:
        message = ['Invalid request']
    error = build_error_model(
        error_message=message,
        error_code='WRONG_FIELD_VALUES')
    log.error(errors=error)
    return build_entity_response(error=error), http_code.BAD_REQUEST


def handle_error_malformed(err):
    message = 'The request content is malformed'
    error = build_error_model(
        error_message=message,
        error_code='MALFORMED_CONTENT')
    log.error(errors=error)
    return build_entity_response(error=error), http_code.BAD_REQUEST


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            if kwargs.get('errors', None):
                error = build_error_model(
                    error_message=kwargs['errors'],
                    error_code='WRONG_FIELD_VALUES')
                log.error(errors=error)
                return build_entity_response(error=error), http_code.BAD_REQUEST
            return func(*args, **kwargs)
        except Exception as e:
            log.error('{}'.format(repr(e)))
            error = dict(error=dict(
                message=[repr(e)], code='UNEXPECTED_EXCEPTION'))
            return error, http_code.INTERNAL_SERVER_ERROR
    return wrapper


def build_async_task_response(task_id):
    '''
    If we're behind proxy, X-Infinidat-Original-Uri holds the original path
    Otherwise, request.url_rule
    Example:
    X-Infinidat-Original-Uri: /api/dde/2/api/network/tools/dig
    request.url_rule: /network/tools/dig
    '''

    base = str(request.url_rule)
    origin = str(request.headers.get('X-Infinidat-Original-Uri', base))
    uri = origin[:-len(base)]

    obj = {
        "metadata": {
            "code": "ACCEPTED",
            "message": "Task ID {} Accepted".format(task_id)
        },
        "result": {
            "task_id": task_id,
            "result_uri": "{}/asynctasks/{}".format(uri, task_id)
        }
    }
    return obj


def _validate_request_values(valid_fields, request_values):
    page_fields = ['page_size', 'page', 'sort']
    try:
        if request_values is None:
            request_values = {}
        for a in request_values.keys():
            if a not in valid_fields and a not in page_fields:
                raise IguardApiQueryException(a)
        per_page = int(request_values.get('page_size', '50'))
        page = int(request_values.get('page', '1'))
        if page < 1 or per_page < 1:
            raise ValueError
        sort_fields = request_values.get("sort", None)
        if sort_fields:
            for field in [a.lstrip('-') for a in sort_fields.split(",")]:
                if field not in valid_fields:
                    raise IguardApiFieldException(field)
    except IguardApiFieldException as e:
        error = build_error_model(
            error_message=[
                'The request contains an unsupported field {}'.format(e)],
            error_code='UNSUPPORTED_FIELD',)
        return build_entity_response(error=error), http_code.BAD_REQUEST
    except IguardApiQueryException as e:
        error = build_error_model(
            error_message=['Wrong query parameter {}'.format(e)],
            error_code='ATTRIBUTE_NOT_FOUND',)
        return build_entity_response(error=error), http_code.BAD_REQUEST
    except ValueError:
        error = build_error_model(
            error_message=['Wrong pagination parameters'],
            error_code='WRONG_FIELD_VALUES',)
        return build_entity_response(error=error), http_code.BAD_REQUEST


def validate_request_values(valid_fields):
    def decorator(f):
        def wrapper(*args, **kwargs):
            request_values = args[-1]
            validate_error = _validate_request_values(
                valid_fields, request_values)
            if not validate_error:
                return f(*args, **kwargs)
            else:
                return validate_error
        return wrapper
    return decorator


def get_user_role() -> Optional[str]:
    return request.headers.get(HEADER_USER)


def allowed_roles(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = get_user_role()
            if user_role is None:
                message = "You are not authorized for this operation, " \
                          "reason: request is missing authorization information."
                log.error(f"{message}, no roles")
                error = build_error_model(
                    error_message=message,
                    error_code='UNAUTHORIZED')
                return build_entity_response(error=error), http_code.UNAUTHORIZED
            if user_role not in roles:
                message = "You are not authorized for this operation, reason: insufficient privileges"
                log.error(f"{message}, received: {user_role} allowed: {roles}")
                error = build_error_model(
                    error_message=message,
                    error_code='UNAUTHORIZED')
                return build_entity_response(error=error), http_code.UNAUTHORIZED
            return func(*args, **kwargs)
        return wrapper
    return decorator


def requires_approval(message: str | Callable):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.args.get('approved', '').lower() == 'true':
                return func(*args, **kwargs)
            else:
                msg = message(*args, **kwargs) if callable(message) else message
                error = build_error_model(
                    error_message=msg,
                    error_code='APPROVAL_REQUIRED')
                return build_entity_response(error=error), HTTPStatus.FORBIDDEN
        return wrapper
    return decorator
