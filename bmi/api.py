from abc import abstractmethod
from abc import ABCMeta

from six import with_metaclass

import numpy as np

# class IBmi(object, metaclass=ABCMeta) can be written
class IBmi(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def __init__(self, engine, configfile=None, *args, **kwargs):
        """
        Construct a new BMI model. Always pass the engine as a configure
        parameter. The configfile can also be passed at this stage
        (for example if you want to use a with statement). You can
        reinitialize with a new configfile by calling initialize

        """
        pass

    @abstractmethod
    def initialize(self, configfile=None):
        """
        Initialize and load the Fortran library (and model, if applicable).
        The Fortran library is loaded and ctypes is used to annotate functions
        inside the library. The Fortran library's initialization is called.
        Normally a path to an ``*.ini`` model file is passed to the
        :meth:`__init__`. If so, that model is loaded. Note that
        :meth:`_load_model` changes the working directory to that of the model.
        """
        pass

    @abstractmethod
    def finalize(self):
        """
        Shutdown the library and clean up the model.
        Note that the Fortran library's cleanup code is not up to snuff yet,
        so the cleanup is not perfect. Note also that the working directory is
        changed back to the original one.
        """
        pass

    @abstractmethod
    def update(self, dt):
        """
        Return type string, compatible with numpy.
        """
        pass

    @abstractmethod
    def get_var_count(self):
        """
        Return number of variables
        """
        pass

    @abstractmethod
    def get_var_name(self, i):
        """
        Return variable name
        """
        pass

    def get_var_type(self, name):
        """
        Return type string, compatible with numpy.
        """
        return self.get_var(name).dtype

    def get_var_rank(self, name):
        """
        Return array rank or 0 for scalar.
        """
        return len(self.get_var(name).shape)

    def get_var_shape(self, name):
        """
        Return shape of the array.
        """
        return self.get_var(name).shape

    @abstractmethod
    def get_start_time(self):
        """
        returns start time
        """
        pass

    @abstractmethod
    def get_end_time(self):
        """
        returns end time of simulation
        """
        pass

    @abstractmethod
    def get_current_time(self):
        """
        returns current time of simulation
        """
        pass

    @abstractmethod
    def get_var(self, name):
        """
        Return an nd array from model library
        """
        pass

    @abstractmethod
    def set_var(self, name, var):
        """Set the variable name with the values of var"""
        pass

    def set_var_slice(self, name, start, count, var):
        """
        Overwrite the values in variable name with data
        from var, in the range (start:start+count).
        Start, count can be integers for rank 1, and can be
        tuples of integers for higher ranks.
        For some implementations it can be equivalent and more efficient to do:
        `get_var(name)[start[0]:start[0]+count[0], ..., start[n]:start[n]+count[n]] = var`
        """
        tmp = self.get_var(name).copy()
        # sometimes we want to slice in 1 dimension, sometimes in more
        # always slice in arrays
        start = np.atleast_1d(start)
        count = np.atleast_1d(count)
        slices = [np.s_[i:(i+n)] for i,n in zip(start, count)]
        tmp[slices] = var
        self.set_var(name, tmp)

    def set_var_index(self, name, index, var):
        """
        Overwrite the values in variable "name" with data
        from var, at the flattened (C-contiguous style)
        indices. Indices is a vector of 0-based
        integers, of the same length as the vector var.
        For some implementations it can be equivalent
        and more efficient to do:
        `get_var(name).flat[index] = var`
        """
        tmp = self.get_var(name).copy()
        tmp.flat[index] = var
        self.set_var(name, tmp)

    @abstractmethod
    def inq_compound(self, name):
        """
        Return the number of fields of a compound type.
        """
        pass

    @abstractmethod
    def inq_compound_field(self, name, index):
        """
        Lookup the type,rank and shape of a compound field
        """
        pass
