import unittest
import mock

class TestMock(object):
    def __init__(self):
        self.mocks = None

    def setup_mocks(self):
        for m in self.mocks:
            try:
                m['mock_name'] = '_'.join(['mock', m['fn'].split('.')[-1]])
                m['patcher_name'] = '_'.join([m['mock_name'], 'patcher'])
                m['patcher'] = mock.patch(m['fn'], autospec=True)
                self.addCleanup(m['patcher'].stop)
                m['mock_fn'] = m['patcher'].start()
                m['mock_fn'].return_value = m.get('rv', None)
                m['mock_fn'].side_effect = m.get('se', None)
            except Exception as e:
                raise e

    def stop_mocks(self):
        for m in self.mocks:
            try:
                m['patcher'].stop
            except Exception as e:
                raise e

    def get_mock(self, name):
        mock_list = [m for m in self.mocks if m['fn'] == name]
        self.assertTrue(len(mock_list) == 1)
        return mock_list[0]

    def check_mocks(self, m=None):
        if m and m.get('n', None):
            self.assertEqual(m['mock_fn'].call_count, m['n'], '{} expected calls: {}, actual calls: {}'.
                             format(m['mock_name'], m['n'], m['mock_fn'].call_count))
            return
        for m in self.mocks:
            self.assertEqual(m['mock_fn'].call_count, m['n'], '{} expected calls: {}, actual calls: {}'.
                             format(m['mock_name'], m['n'], m['mock_fn'].call_count))
        return
