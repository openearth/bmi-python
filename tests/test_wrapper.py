import logging
import unittest
import nose
import numpy.testing as npt
import numpy as np
try:
    import mock
except ImportError:
    pass

import bmi.wrapper
bmi.wrapper.BMIWrapper.known_paths += ['tests']

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestCase(unittest.TestCase):
    engine = "modelfortran"
    def setUp(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine=self.engine,
                                              configfile="model.ini")

    @mock.patch('platform.system', lambda: 'Linux')
    def test_libname1(self):
        self.assertEqual(self.wrapper._libname(), 'lib%s.so' % (self.engine, ))

    @mock.patch('platform.system', lambda: 'Darwin')
    def test_libname2(self):
        self.assertEqual(self.wrapper._libname(), 'lib%s.dylib' % (self.engine, ))

    @mock.patch('platform.system', lambda: 'Windows')
    def test_libname3(self):
        self.assertEqual(self.wrapper._libname(), '%s.dll' % (self.engine, ))

    def test_initialize(self):
        self.wrapper.initialize()

    def test_finalize(self):
        self.wrapper.initialize()
        self.wrapper.finalize()

    def test_with(self):
        with self.wrapper:
            pass

    def test_update(self):
        with self.wrapper as model:
            model.update()

    def test_start_time(self):
        with self.wrapper as model:
            self.assertEqual(0, model.get_start_time())

    def test_current_time(self):
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())

    def test_end_time(self):
        with self.wrapper as model:
            self.assertEqual(10, model.get_end_time())

    def test_update_time(self):
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())
            model.update(1.0)
            self.assertEqual(1, model.get_current_time())

    def test_update_twice(self):
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())
            model.update(1)
            self.assertEqual(1, model.get_current_time())
            model.update(5)
            self.assertEqual(6, model.get_current_time())

    def test_get_var(self):
        with self.wrapper as model:
            arr1 = model.get_var('arr1')
            npt.assert_allclose(arr1, [3,2,1])
    def test_set_var(self):
        with self.wrapper as model:
            for name in ('arr1', 'arr2', 'arr3'):
                arr = model.get_var(name)
                zeros = np.zeros_like(arr)
                model.set_var(name, zeros)
                arr_a = model.get_var(name)
                npt.assert_allclose(arr_a, zeros)

    def test_set_var_slice(self):
        with self.wrapper as model:
            a = model.get_var('arr1').copy()
            values = np.array([5], dtype=a.dtype)
            model.set_var_slice('arr1', (0, ), (1,), values.copy())
            b = model.get_var('arr1').copy()
            a[0] = 5
            npt.assert_allclose(a, b)

    def test_set_logger(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="modelc",
                                              configfile="model.ini")
        # find the model in this directory
        logger = logging.getLogger('test')
        self.wrapper.set_logger(logger)
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())
            model.update()


class TestCreateStringBuffer(unittest.TestCase):
    def test_create_string_buffer(self):
        bmi.wrapper.create_string_buffer(4)
        bmi.wrapper.create_string_buffer(b'test')
        bmi.wrapper.create_string_buffer('test')
        bmi.wrapper.create_string_buffer(u'test')



if __name__ == '__main__':
    nose.main()
