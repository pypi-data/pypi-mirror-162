import os
import logging
import json
import unittest
import ddt
from infiniguard_api.common import const, messages
from infiniguard_api.tst.base.test_base import TestBase


@ddt.ddt
class TestVerifyNode(TestBase):
    log_tests = True

    def setUp(self):
        os.environ['INFINIGUARD_REBOOT'] = "0"
        pass

    def tearDown(self):
        pass

    def testRebootSuccess(self):
        rv = self.__class__.app.post('/misc/reboot')
        self.assertEqual(rv.status_code, 200)
        resp = json.loads(rv.data)
        message = resp.pop('message')
        self.assertEqual(message, messages.DDE_REBOOTING_MSG.format(const.REBOOT_WAIT_TIME_S))


def _cmp(x, y):
    return (x > y) - (x < y)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = lambda x, y: (_cmp(x, y) if '_' in x and '_' in y
                                                              and x.split('_')[0] == y.split('_')[0] else _cmp(y, x))
    loader.testMethodPrefix = "test"  # default value is "test"
    suite = loader.loadTestsFromTestCase(TestVerifyNode)
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
