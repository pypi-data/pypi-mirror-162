import os
import unittest
import mock
from infiniguard_api.api_server.infiniguard_api_app import infiniguard_api_app


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        try:
            cls.app = infiniguard_api_app.test_client()
            os.environ['INFINIGUARD_API_MOCK'] = "1"
            os.environ['CLI_OUTPUT_DIR'] = '../cli_output'
            os.environ['RESPONSE_DIR'] = '../responses'
        except Exception as e:
            cls.tearDownClass()
            raise e

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def shortDescription(self):
        return None

