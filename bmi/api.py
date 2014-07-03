from abc import abstractmethod
from abc import ABCMeta


class IBmi(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self):
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
    def set_logger(self, logger):
        """
        subscribe to fortran log messages
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

    @abstractmethod
    def get_var_type(self, name):
        """
        Return type string, compatible with numpy.
        """
        pass

    @abstractmethod
    def get_var_rank(self, name):
        """
        Return array rank or 0 for scalar.
        """
        pass

    @abstractmethod
    def get_var_shape(self, name):
        """
        Return shape of the array.
        """
        pass

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
        pass

    @abstractmethod
    def set_var_slice(self, name, start, count, var):
        pass

    @abstractmethod
    def inq_compound(self, name):
        """
        Return the number of fields and size (not yet) of a compound type.
        """
        pass

    @abstractmethod
    def inq_compound_field(self, name, index):
        """
        Lookup the type,rank and shape of a compound field
        """
        pass

    @abstractmethod
    def make_compound_ctype(self, varname):
        """
        Create a ctypes type that corresponds to a compound type in memory.
        """
        pass

    @abstractmethod
    def set_structure_field(self, name, id, field, value):
        pass
