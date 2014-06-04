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
    def setUp(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="modelc",
                                              configfile="model.ini")

    @mock.patch('platform.system', lambda: 'Linux')
    def test_libname1(self):
        self.assertEquals(self.wrapper._libname(), 'libmodelc.so')

    @mock.patch('platform.system', lambda: 'Darwin')
    def test_libname2(self):
        self.assertEquals(self.wrapper._libname(), 'libmodelc.dylib')

    @mock.patch('platform.system', lambda: 'Windows')
    def test_libname3(self):
        self.assertEquals(self.wrapper._libname(), 'modelc.dll')

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
            model.update()
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
            arr1 = model.get_var('arr1').copy()
            values = np.array([5], dtype=arr1.dtype)
            model.set_var_slice('arr1', (0,), (1,), values)
            arr1a = model.get_var('arr1')
            arr1[0] = 5
            logger.info(arr1a)
            npt.assert_allclose(arr1a, arr1)

    def test_set_logger(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="modelc",
                                              configfile="model.ini")
        # find the model in this directory
        logger = logging.getLogger('test')
        self.wrapper.set_logger(logger)
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())
            model.update()


if __name__ == '__main__':
    nose.main()
