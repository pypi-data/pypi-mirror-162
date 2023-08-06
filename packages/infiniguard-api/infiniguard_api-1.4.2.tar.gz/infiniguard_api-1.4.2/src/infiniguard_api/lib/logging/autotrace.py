# Copyright (c) 2010-2011 Jan Kaliszewski (zuo). All rights reserved.
# Licensed under the MIT License. Python 2.6/2.7-compatibile.

import os.path
import sys
import six
from contextlib import contextmanager
from six.moves import reprlib

__all__ = 'trace_logging_on',

default_refdir = os.path.dirname(sys.modules['__main__'].__file__)

def trace_logging_on(logger='',
                     loggermethod='debug',
                     reprfunc=default_reprfunc,
                     refdir=default_refdir,
                     filterarg='',
                     events2log=None,
                     negprefix=('..', '<'),
                     filterfunc=(lambda s: True)
                     ):
    """
    Enable logging of Python call/return/exception events (handily filtered).

    :param logger: logger name or instance
    :param loggermethod: logger method name
    :param reprfunc: repr()-replacement function
    :param refdir: reference-point directory path
    :param negprefix: negative filtering path prefixes
    :param filterfunc: custom filtering function
    :param filterarg: .format()-able filter argument pattern, ex. '{event}&{path}&{frame.f_lineno}'
    :param events2log: mapping events to .format()-able log pattern, which refer to tracer()'s locals, ex. '{event}&{path}&{frame.f_lineno}'

    Usage variants:
    * simply-turn-on call:        trace_logging_on(...)
    * context manager syntax:     with trace_logging_on(...): ...
    * context manager with 'as':  with trace_logging_on(...) as tracefunc: ...
    """

    from inspect import getargvalues, formatargvalues
    from traceback import format_exception

    if isinstance(logger, six.string_types):
        from .iguard_logging import getLogger as get_logger
        logger = get_logger(logger)

    log = getattr(logger, loggermethod)

    relpath = os.path.relpath
    formatvalue = (lambda s: '=' + reprfunc(s))

    filterarg_format = filterarg.format

    if events2log is None:
        events2log = {
            'call': '[C  ] {path}: {name}{callargs}',
            'return': '[  R] {path}: {name}  ->  {argrepr}',
            'exception': '[ E ] {path}, in {name}:\n{traceback}',
        }

    def tracer(frame, event, arg):
        # initial event filtering
        if event not in events2log:
            return tracer
        path = relpath(frame.f_code.co_filename, refdir)  # relative to refdir

        # path-prefix-based scope filtering (negative, i.e. False lets by)
        if path.startswith(negprefix):
            return None  # (<- None to discontinue tracing in sub-scopes)

        # adding some locals (to be used to format filtering/logging arguments)
        name = frame.f_code.co_name
        argrepr = reprfunc(arg)

        if event == 'call':
            argvalues = (getargvalues(frame) if name != '<genexpr>' else ([],) + getargvalues(frame)[1:])
            callargs = formatargvalues(*argvalues, formatvalue=formatvalue)
        elif event == 'exception':
            traceback = ''.join(format_exception(*arg))

        pattern_fields = locals()

        # callback-based individual filtering (positive, i.e. True lets by)
        if not filterfunc(filterarg_format(**pattern_fields)):
            return tracer

        # event-specific logging
        log(events2log[event].format(**pattern_fields))
        return tracer

    with_support = [_with_statement_support(tracer, previous=sys.gettrace())]
    sys.settrace(tracer)
    return with_support.pop()


@contextmanager
def _with_statement_support(tracer, previous):
    yield tracer
    sys.settrace(previous)


def main():
    ## Example script ##
    from . import iguard_logging
    from operator import methodcaller


    def robin(a, b, c):
        return c, b, a


    def lancelot(x, y="Let's not bicker and argue", z="about who killed who."):
        return x, y, z


    def rabbit():
        return 1 / 0


    def arthur(nee):
        lancelot('Camelot!')
        robin('Oh, shut up', 'and go', 'and change your armor!')
        robin(*lancelot("Why doesn't Lancelot go?"))
        # noinspection PyBroadException
        try:
            rabbit()
        except:
            lancelot(*robin('spam', 'spam', 'spam'))
        return nee

    iguard_logging.basicConfig(level=iguard_logging.DEBUG)

    arthur(0)  # (<- not logged)

    with trace_logging_on(logger='tim.the.enchanter', reprfunc='.:{0}:.'.format):
        arthur(1)

        with trace_logging_on(refdir='/usr', negprefix=(), filterarg='{event}', filterfunc= (lambda s: s == 'call')):
            arthur('2 sheds')

        arthur(3)

    arthur(4)  # (<- not logged)

    trace_logging_on(filterarg='{name}',
                     filterfunc=methodcaller('startswith', 'r'),
                     logger='comfy.chair', loggermethod='info', reprfunc=repr)
    arthur(5)


if __name__ == '__main__':
    main()