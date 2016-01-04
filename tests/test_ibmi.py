import logging
import unittest

from bmi.api import IBmi

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TooSimpleModel(IBmi):
    def __init__(self, engine='model', configfile='', *args, **kwargs):
        pass


class SimpleModel(IBmi):
    def __init__(self, engine='model', configfile='', *args, **kwargs):
        self.engine = engine
        self.configfile = configfile

        self.start_time = 0.0
        self.end_time = 10.0
        self.time_step = 1.0

    def initialize(self, configfile=None):
        self.configfile = configfile

    def finalize(self):
        pass

    def update(self, dt=-1):
        if dt != -1:
            self.current_time += dt
        else:
            self.current_time += self.time_step

    def get_current_time(self):
        return self.t

    def get_end_time(self):
        return self.end_time

    def get_start_time(self):
        return self.start_time

    def get_var(self, var_name):
        raise ValueError("I do not have variables")

    def get_var_count(self):
        return 0

    def get_var_name(self, i):
        return IndexError("I do not have variables")

    def set_var(self, var_name, value):
        raise ValueError("I do not have variables")

    def inq_compound(self, typename):
        raise ValueError("I do not have custom types")

    def inq_compound_field(self, typename, fieldname):
        raise ValueError("I do not have custom types")


class TestCase(unittest.TestCase):
    engine = "model"

    def setUp(self):
        pass

    def test_engine_missing_methods(self):
        with self.assertRaises(TypeError):
            self.model = TooSimpleModel(engine='model')

    def test_engine_all_methods(self):
        self.model = SimpleModel(engine='model')

    def test_engine_engine_set(self):
        self.model = SimpleModel(engine='model')
        self.assertEqual(self.model.engine, 'model')
