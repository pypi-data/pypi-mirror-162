import six
import json
import os
import unittest

import ddt
from infiniguard_api.common import messages
from infiniguard_api.tst.base.test_base import TestBase


class MyDict(dict):
    pass


def annotated(dict_in, qualifier=None):
    r = MyDict(dict_in)
    name = "test_bad_{}".format(list(r)[0])
    name = "{}_{}".format(name, qualifier) if qualifier else name
    setattr(r, "__name__", name)
    return r


@ddt.ddt
class TestVerifyNetcfg(TestBase):
    log_tests = False

    def setUp(self):
        super(TestVerifyNetcfg, self).setUp()
        self.session = self.__class__.app.session_transaction()
        self.endpoint = '/network/netcfg/'
        pass

    def tearDown(self):
        pass

    def testGetNetcfgSuccess(self):
        rv = self.__class__.app.get(self.endpoint)
        self.assertEqual(rv.status_code, 200)

        with open(os.path.join(os.environ.get('RESPONSE_DIR', ''), 'netcfg.json')) as fp:
            self.assertDictEqual(json.loads(rv.data), json.load(fp))

    @ddt.data('p4p1', 'p4p1:1', 'bond0:1')
    def testGetNetcfgWithDevnameSuccess(self, devname):
        rv = self.__class__.app.get('{}{}'.format(self.endpoint, devname))
        self.assertEqual(rv.status_code, 200)

        filename = devname.replace(':', '_').replace('.', '_')
        with open(os.path.join(os.environ.get('RESPONSE_DIR', ''), 'netcfg_{}.json'.format(filename))) as fp:
            self.assertDictEqual(json.loads(rv.data), json.load(fp))

    @ddt.data(
        {"devname": "p4p1:1", "ipaddr": "10.10.1.2", "netmask": "255.255.255.0", "gateway": "10.10.1.1",
         "defaultgw": "YES"},
        {"devname": "bond0:1", "ipaddr": "10.10.1.2", "netmask": "255.255.255.0", "gateway": "10.10.1.1",
         "defaultgw": "YES", "slaves": ["p4p3", "p4p4"], "mode": "RR"},
    )
    def testCreateNetcfgSuccess(self, parms):
        if os.environ.get('INFINIGUARD_API_MOCK', "0") != "1":
            rv = self.__class__.app.get('{}{}'.format(self.endpoint, parms['devname']))
            if rv.status_code == 200 and rv.data and json.loads(rv.data)['result']:
                rv = self.__class__.app.delete('{}{}'.format(self.endpoint, parms['devname']))
                self.assertEqual(rv.status_code, 204)

        rv = self.__class__.app.post(self.endpoint, data=json.dumps(parms), content_type='application/json')
        self.assertEqual(rv.status_code, 201)
        resp = json.loads(rv.data)
        message = resp.pop('message')
        self.assertEqual(message, messages.DDE_REBOOT_MSG)

        filename = parms['devname'].replace(':', '_').replace('.', '_')
        with open(os.path.join(os.environ.get('RESPONSE_DIR', ''), 'netcfg_{}.json'.format(filename))) as fp:
            self.assertDictEqual(resp, json.load(fp))

    @ddt.data('p4p1:1', 'bond0.12:2')
    def testDeleteNetcfgSuccess(self, devname):
        rv = self.__class__.app.get('{}{}'.format(self.endpoint, devname))
        if rv.status_code == 200 and rv.data and json.loads(rv.data)['result']:
            rv = self.__class__.app.delete('{}{}'.format(self.endpoint, devname))
            self.assertEqual(rv.status_code, 200)

    @ddt.data(
        annotated({"defaultgw": "HOHOHO"}),
        annotated({"ipaddr": 10}),
        annotated({"netmask": 255}),
        annotated({"gateway": 10}),
        annotated({"mode": "HOHOHO"}),
        annotated({"slaves": []}, "empty"),
        annotated({"slaves": [{}]}, "one"),
    )
    def testCreateNetcfgFailure(self, error):
        parms = {"devname": "bond0:1", "ipaddr": "10.10.1.2", "netmask": "255.255.255.0", "gateway": "10.10.1.1",
                 "defaultgw": "YES", "slaves": "p4p3,p4p4", "mode": "RR"}
        parms.update(error)
        rv = self.__class__.app.post(self.endpoint, data=json.dumps(parms), content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        resp = json.loads(rv.data)
        '''make sure error message is of format:
            {
              "error": {
                "code": "WRONG_FIELD_VALUES",
                "message": [
                  "{}: some string".format(error.keys()[0])
                ]
              }
            }
        '''
        self.assertIn('error', resp)
        self.assertIn('code', resp['error'])
        self.assertEqual(resp['error']['code'], "WRONG_FIELD_VALUES")
        self.assertIn('message', resp['error'])
        self.assertTrue(len(list(error.keys())) >= 1)
        self.assertTrue(len(resp['error']['message']) >= 1)
        for returned, expected in list(zip(resp['error']['message'], error)):
            self.assertIn(expected, returned)


def _cmp(x, y):
    return (x > y) - (x < y)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = lambda x, y: (_cmp(x, y) if '_' in x and '_' in y and
                                                              x.split('_')[0] == y.split('_')[0] else (_cmp(y, x)))
    loader.testMethodPrefix = "test"  # default value is "test"
    suite = loader.loadTestsFromTestCase(TestVerifyNetcfg)
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
