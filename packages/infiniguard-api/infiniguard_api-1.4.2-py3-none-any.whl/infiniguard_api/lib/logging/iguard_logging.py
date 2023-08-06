import errno
import os
import wrapt
import sys
import structlog
import logging
from logbook import (
    RotatingFileHandler,
    CRITICAL,
    WARNING,
    INFO,
    DEBUG,
    set_datetime_format,
    NestedSetup,
    NullHandler,
    Logger
)
from logbook.more import ColorizedStderrHandler
from logbook.compat import redirect_logging

from infiniguard_api.common.const import (
    LOGFILE,
    MAX_LOGFILE_SIZE,
    MAX_LOGFILES
)


def get_logger(*args, **kwargs):
    return structlog.get_logger(*args, **kwargs)


def setup_lib_logging():
    redirect_logging()
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)


def setup_application_logger(
        console_level=INFO,
        file_level=DEBUG,
        logfile=LOGFILE,
        max_file_size=MAX_LOGFILE_SIZE,
        max_files=MAX_LOGFILES
):
    set_datetime_format('local')

    logfile_path = os.path.dirname(logfile)
    try:
        os.makedirs(logfile_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    file_handler = RotatingFileHandler(
        logfile,
        max_size=max_file_size,
        backup_count=max_files,
        level=file_level,
        bubble=True
    )

    stderr_handler = ColorizedStderrHandler(
        level=console_level,
        bubble=True
    )

    loggers = [
        NullHandler(),
        stderr_handler,
        file_handler,
    ]

    setup_lib_logging()

    def logger_factory(*args, **kwargs):
        return Logger(*args, **kwargs)

    structlog.configure_once(
        processors=[
            structlog.processors.KeyValueRenderer(
                sort_keys=True,
                key_order=['event'],
                drop_missing=True
            )
        ],
        logger_factory=logger_factory,
    )

    handle = NestedSetup(loggers)
    return handle


def context(message):
    """
    Decorator to add logging context to a method or a function.
    Logs entrance and calling parameters

    :param message: message to log on entering context
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        log = get_logger().bind(
            obj=instance,
            context=wrapped.__name__,
            args=args,
            kwargs=kwargs
        )
        log.trace(message)
        return wrapped(*args, **kwargs)

    return wrapper


def reraise(as_exception, message=None):
    """
    Decorator to execute wrapped function in a try...except block
    Log an exception with a traceback and reraise as 'as_exception'
    :param as_exception: Exception to raise
    :param message: log.error message, also passed to an exception
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        log = get_logger().bind(
            obj=instance,
            context=wrapped.__name__,
            args=args,
            kwargs=kwargs
        )
        try:
            return wrapped(*args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = message if message else e
            log.exception(e)
            raise as_exception(error_message)

    return wrapper


@wrapt.decorator
def log_exception(wrapped, instance, args, kwargs):
    log = get_logger().bind(
        obj=instance,
        context=wrapped.__name__,
        args=args,
        kwargs=kwargs
    )
    try:
        return wrapped(*args, **kwargs)
    except Exception as e:
        log.exception(e)
        raise


def noreraise(under_test_only=False):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        try:
            return wrapped(*args, **kwargs)
        except Exception as e:
            from ..tests.fixtures import is_under_test
            if under_test_only and not is_under_test():
                raise
            else:
                pass

    return wrapper

