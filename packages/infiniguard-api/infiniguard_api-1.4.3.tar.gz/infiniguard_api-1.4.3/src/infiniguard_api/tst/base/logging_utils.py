import unittest
import six
import logging


class LoggedTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.logger = logging.getLogger("")
        # cls.logger.setLevel(logging.INFO)
        # if not cls.log_tests:
        #     cls.logger.addHandler(NullHandler())
        cls.logger = logging.getLogger("")
        cls.logger.setLevel(logging.INFO)
        if cls.log_tests:
            if not cls.logger.handlers:
                print("No loggers?")
                pass
        else:
            cls.logger.addHandler(logging.NullHandler)

    @classmethod
    def tearDownClass(cls):
        if cls.log_tests:
            for h in cls.logger.handlers:
                cls.logger.removeHandler(h)
        else:
            cls.logger.addHandler(NullHandler())
