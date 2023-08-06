import six
import os
import json
import unittest
import ddt

class TestSchema2Class(unittest.TestCase):
    log_tests = True

    def setUp(self):
        os.environ['RESPONSE_DIR'] = '../responses'
        pass

    def tearDown(self):
        pass

    @staticmethod
    def validate_data(data, validation_schema):
        try:
            netcfg = validation_schema().load(data)
            return None, netcfg.data
        except ValidationError as e:
            log.error(e.message)
            errmsg = ['{}:{}'.format(k, v) for error in list(e.values()) for (k, v) in error.items()]
            error = dict(message=errmsg, code='WRONG_FIELD_VALUES')
            return error, None
        except Exception as e:
            log.error(e.message)
            error = dict(message=e.message, code='UNEXPECTED_VALIDATION_ERROR')
            return error, None

    def testBaseSchema(self):
        os.environ['USE_SCHEMA'] = 'BASE_SCHEMA'
        from infiniguard_api.model import netcfg_schemas
        with open(os.path.join(os.environ.get('RESPONSE_DIR', ''), 'netcfg.json')) as fp:
            data = json.load(fp)
        error, netcfg = self.validate_data(data['result']['NetworkCfg'], netcfg_schemas.NetworkCfgSchema)
        if error:
            return dict(error=error), 400
        netcfg.dict = data['result']
        pass

if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.testMethodPrefix = "test"  # default value is "test"
    suite = loader.loadTestsFromTestCase(TestSchema2Class)
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
