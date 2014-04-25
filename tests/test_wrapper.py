import nose
import mock
import unittest
import bmi.wrapper


class TestCase(unittest.TestCase):
    def setUp(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="model")

    @mock.patch('platform.system', lambda: 'Linux')
    def test_libname1(self):
        self.assertEquals(self.wrapper._libname(), 'libmodel.so')

    @mock.patch('platform.system', lambda: 'Darwin')
    def test_libname2(self):
        self.assertEquals(self.wrapper._libname(), 'libmodel.dylib')

    @mock.patch('platform.system', lambda: 'Windows')
    def test_libname3(self):
        self.assertEquals(self.wrapper._libname(), 'model.dll')


if __name__ == '__main__':
    nose.main()
