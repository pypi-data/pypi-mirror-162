import os


class Config(object):
    DEBUG = False
    TESTING = False
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False
    RESULTS_PER_PAGE = 50
    MAX_RESULTS_PER_PAGE = 100
    LOGGER_HANDLER_POLICY = 'never'     # flask logging

class DevelopmentConfig(Config):
    DEBUG = False
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False
    LOG_TO_STDERR = True
