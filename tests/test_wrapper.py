import ctypes
import os
import nose
from nose import with_setup
import mock
import unittest
import bmi.wrapper

class TestCase(unittest.TestCase):

    def setUp(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="subgrid")
    @mock.patch('platform.system', lambda: 'Linux')
    def test_libname1(self):
        self.assertEquals(self.wrapper._libname(), 'libsubgrid.so')

    @mock.patch('platform.system', lambda: 'Darwin')
    def test_libname2(self):
        self.assertEquals(self.wrapper._libname(), 'libsubgrid.dylib')

    @mock.patch('platform.system', lambda: 'Windows')
    def test_libname3(self):
        self.assertEquals(self.wrapper._libname(), 'subgrid.dll')


if __name__ == '__main__':
    nose.main()
