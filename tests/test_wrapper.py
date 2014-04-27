import logging
import unittest

import nose
import mock

import bmi.wrapper
bmi.wrapper.BMIWrapper.known_paths += ['tests']

logging.basicConfig(level=logging.DEBUG)


class TestCase(unittest.TestCase):
    def setUp(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="model",
                                              configfile="model.ini")

    @mock.patch('platform.system', lambda: 'Linux')
    def test_libname1(self):
        self.assertEquals(self.wrapper._libname(), 'libmodel.so')

    @mock.patch('platform.system', lambda: 'Darwin')
    def test_libname2(self):
        self.assertEquals(self.wrapper._libname(), 'libmodel.dylib')

    @mock.patch('platform.system', lambda: 'Windows')
    def test_libname3(self):
        self.assertEquals(self.wrapper._libname(), 'model.dll')

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
            model.update()
            self.assertEqual(1, model.get_current_time())

    def test_update_twice(self):
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())
            model.update()
            self.assertEqual(1, model.get_current_time())
            model.update(5)
            self.assertEqual(6, model.get_current_time())

    def test_set_logger(self):
        self.wrapper = bmi.wrapper.BMIWrapper(engine="model",
                                              configfile="model.ini")
        # find the model in this directory
        logger = logging.getLogger('test')
        self.wrapper.set_logger(logger)
        with self.wrapper as model:
            self.assertEqual(0, model.get_current_time())
            model.update()


if __name__ == '__main__':
    nose.main()
