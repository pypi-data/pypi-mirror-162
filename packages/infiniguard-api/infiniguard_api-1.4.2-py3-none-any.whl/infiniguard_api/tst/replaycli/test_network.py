import json
import os
import unittest

from ddt import data, ddt, file_data
from infiniguard_api.common import messages
from infiniguard_api.tst.base.test_base import TestBase
from infiniguard_api.lib.rest.common import http_code


@ddt
class TestVerifyNetwork(TestBase):
    log_tests = False

    def setUp(self):
        super(TestVerifyNetwork, self).setUp()
        self.session = self.__class__.app.session_transaction()
        self.response_map = {'host': 'hostcfg', }
        self.base = '/network'
        self.maxDiff = None

    def tearDown(self):
        pass

    def getResponseExpected(self, obj, devname=None):
        filename = '{}'.format(self.response_map.get(obj, obj))
        filename = '{}_{}'.format(filename, devname) if devname else '{}'.format(filename)
        filename = filename.replace('.', '_').replace(':', '_') + '.json'
        with open(os.path.join(os.environ.get('RESPONSE_DIR', ''), filename)) as fp:
            expected = json.load(fp)
            expected = expected['result']
        return expected

    def verifyResponse(self, response, obj, devname=None):
        returned = json.loads(response)
        self.assertIsNotNone(returned)
        returned = returned.get('result')
        self.assertIsNotNone(returned)
        expected = self.getResponseExpected(obj, devname)

        if isinstance(returned, dict):
            self.assertDictEqual(returned, expected)
        elif isinstance(returned, list):
            self.assertEqual(len(returned), len(expected))
            for d in returned:
                self.assertIn(d, expected)
            [self.assertIn(d, expected) for d in returned]
        else:
            self.assertTrue(True)

    @file_data('data/network/create_success.json')
    def test10CreateSuccess(self, parms):
        request, obj, filename = parms
        rv = self.__class__.app.post('{}/{}/'.format(self.base, obj), data=json.dumps(request),
                                     content_type='application/json')
        self.assertEqual(rv.status_code, http_code.ACCEPTED)
        resp = json.loads(rv.data)
        if obj != 'host':
            message = resp.pop('message')
            self.assertEqual(message, messages.DDE_REBOOT_MSG)
        with open(os.path.join(os.environ.get('RESPONSE_DIR', ''), filename)) as fp:
            expected = json.load(fp)
            if isinstance(expected['result'], list):
                expected['result'] = expected['result'][0]
            self.assertDictEqual(resp, expected)

    @file_data('data/network/create_failure.json')
    def test20CreateFailure(self, parms):
        obj, error, request = parms
        rv = self.__class__.app.post('{}/{}/'.format(self.base, obj), data=json.dumps(request),
                                     content_type='application/json')
        self.assertEqual(rv.status_code, http_code.BAD_REQUEST)
        resp = json.loads(rv.data)
        '''make sure error message is of format:
            {
              "error": {
                "code": "BAD_REQUEST",
                "message": [
                  "{}: some string".format(error.keys()[0])
                ]
              }
            }
        '''
        self.assertIn('error', resp)
        self.assertIn('code', resp['error'])
        self.assertEqual(resp['error']['code'], "BAD_REQUEST")
        self.assertIn('message', resp['error'])
        self.assertTrue(len(list(resp['error'].keys())) >= 1)
        self.assertTrue(len(resp['error']['message']) >= 1)
        m = list(zip(resp['error']['message'], [error]))
        for returned, expected in m:
            self.assertIn(expected, returned)

    @file_data('data/network/get_success.json')
    def test30GetSuccess(self, parms):
        obj, devname = parms
        endpoint = '{}/{}/'.format(self.base, obj)
        endpoint = '{}{}'.format(endpoint, devname) if devname else endpoint
        rv = self.__class__.app.get(endpoint)
        self.assertEqual(rv.status_code, http_code.OK)
        self.verifyResponse(rv.data, obj, devname)

    @file_data('data/network/delete_success.json')
    def test40DeleteSuccess(self, parms):
        obj, name = parms
        rv = self.__class__.app.delete('{}/{}/{}'.format(self.base, obj, name))
        self.assertEqual(rv.status_code, http_code.ACCEPTED)
        resp = json.loads(rv.data)
        message = resp.pop('message')
        self.assertIn(messages.DDE_REBOOT_MSG, message)

    @unittest.skip('Not supported in this release')
    @data('backup', 'restore')
    def test50MiscSuccess(self, cmd):
        rv = self.__class__.app.post('{}/{}'.format(self.base, cmd))
        self.assertEqual(rv.status_code, http_code.OK)
        resp = json.loads(rv.data)
        message = resp.pop('message')
        if cmd == 'backup':
            self.assertEqual(message, messages.NETCFG_BACKUP)
        else:
            self.assertEqual(message, messages.NETCFG_RESTORE)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.testMethodPrefix = "test"
    suite = loader.loadTestsFromTestCase(TestVerifyNetwork)
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
