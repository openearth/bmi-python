"""
This module provides a ctypes wrapper around a bmi library.

"""

from __future__ import print_function
import functools
import io
import logging
import os
import multiprocessing          # for shared memory
import platform
import sys

import faulthandler

from numpy.ctypeslib import ndpointer  # nd arrays
import numpy as np
import pandas

logger = logging.getLogger(__name__)

from ctypes import (
    # Types
    c_double, c_int, c_char_p, c_bool, c_char, c_float, c_void_p,
    # Complex types
    ARRAY, Structure,
    # Making strings
    # Pointering
    POINTER, byref, CFUNCTYPE,
    # Loading
    cdll
)


# Custom version of create_string_buffer that also accepts py3 strings.
def create_string_buffer(init, size=None):
    """create_string_buffer(aBytes) -> character array
    create_string_buffer(anInteger) -> character array
    create_string_buffer(aString, anInteger) -> character array
    """
    # a create_string_buffer that works...
    if isinstance(init, (str, bytes)):
        if size is None:
            size = len(init)+1
        buftype = c_char * size
        buf = buftype()
        if isinstance(init, bytes):
            buf.value = init
        else:
            # just work....
            buf.value = init.encode(sys.getdefaultencoding())
        return buf
    elif isinstance(init, int):
        buftype = c_char * init
        buf = buftype()
        return buf
    raise TypeError(init)


# maximum rank
MAXDIMS = 6
# This should be the same as in the modelapi
MAXSTRLEN = 1024

# map c types to ctypes types
# For python3 every string exchanged with fortran is bytes
CTYPESMAP = {
    b'bool': c_bool,
    b'char': c_char,
    b'double': c_double,
    b'float': c_float,
    b'int': c_int
}
# map c types to numpy types
TYPEMAP = {
    b"bool": "bool",
    b"char": "S",
    b"double": "double",
    b"float": "float32",
    b"int": "int32"
}


def struct2dict(struct):
    """convert a ctypes structure to a dictionary"""
    return {x: getattr(struct, x) for x in dict(struct._fields_).keys()}


def structs2records(structs):
    """convert one or more structs and generate dictionaries"""
    try:
        n = len(structs)
    except TypeError:
        # no array
        yield struct2dict(structs)
        # just 1
        return
    for i in range(n):
        struct = structs[i]
        yield struct2dict(struct)


def structs2pandas(structs):
    """convert ctypes structure or structure array to pandas data frame"""
    records = list(structs2records(structs))
    df = pandas.DataFrame.from_records(records)
    # TODO: do this for string columns, for now just for id
    # How can we check for string columns, this is not nice:
    # df.columns[df.dtypes == object]
    if 'id' in df:
        df["id"] = df["id"].apply(str.rstrip)
    return df


SHAPEARRAY = ndpointer(dtype='int32',
                       ndim=1,
                       shape=(MAXDIMS,),
                       flags='F')


try:
    faulthandler.enable()
except io.UnsupportedOperation:
    # In notebooks faulthandler does not work.
    pass
except AttributeError:
    # In notebooks faulthandler does not work.
    pass


# Wrap these functions
FUNCTIONS = [
    {
        'name': 'update',
        'argtypes': [POINTER(c_double)],
        'restype': c_int,
    },
    {
        'name': 'initialize',
        'argtypes': [],
        'restype': c_int,
    },
    {
        'name': 'finalize',
        'argtypes': [],
        'restype': c_int,
    }
]


class BMIWrapper(object):
    """Wrapper around a ctypes-loaded BMI library.

    There are two ways to use the wrapper. A handy way is as a context
    manager, so with a ``with`` statement::

        with BMIWrapper(config='/full/path/model.ini') as model:
            # model is the wrapper around library.
            model.update(1.0)

    The second way is by calling :meth:`start` and :meth:`stop` yourself and
    using the :attr:`library` attribute to access the Fortran library::

        wrapper = BMIWrapper(config='/full/path/model.ini')
        wrapper.initalize()
        wrapper.update(1.0)
        ...
        wrapper.finalize()

    Note: Without the ``config`` argument, no model is loaded and you're free to
    use the library as you want.

    """
    library = None

    def __init__(self, engine=None, configfile=None):
        """Initialize the class.

        The ``engine`` argument should be the path to a model's ``engine``
        file, which is the library name without lib suffix and dylib/dll/so suffix.
        The ``config`` argument should be the path to a model's ``*.config``
        file.

        Nothing much should happen here so that the code remains easy to
        test. Most of the library-related initialization happens in the
        :meth:`initialize` method.
        """
        self.engine = engine
        self.configfile = configfile
        self.original_dir = os.getcwd()

        self.known_paths = [
            # From very specific to generic. Local installs win,
            # and /opt/modelname wins over system installs.
            '.',
            '~/local/lib',
            '~/.local/lib',
            '/opt/{}/lib'.format(self.engine),
            '/usr/local/lib',
            '/usr/lib',
        ]

    def _libname(self):
        """Return platform-specific modelf90 shared library name."""
        prefix = 'lib'
        suffix = '.so'
        if platform.system() == 'Darwin':
            suffix = '.dylib'
        if platform.system() == 'Windows':
            prefix = ''
            suffix = '.dll'
        return prefix + self.engine + suffix

    def _library_path(self):
        """Return full path to the shared library.

        A couple of regular unix paths like ``/usr/lib/`` is searched by
        default. If your library is not in one of those, set a
        ``LD_LIBRARY_PATH`` environment variable to the directory with your
        shared library.

        If the library cannot be found, a ``RuntimeError`` with debug
        information is raised.
        """

        pathname = 'LD_LIBRARY_PATH'
        separator = ':'
        if platform.system() == 'Darwin':
            pathname = 'DYLD_LIBRARY_PATH'
            separator = ':'
        if platform.system() == 'Windows':
            # windows does not separate between dll path's and exe paths
            pathname = 'PATH'
            separator = ';'

        lib_path_from_environment = os.environ.get(pathname, '')
        # Expand the paths with the system path if it exists
        if lib_path_from_environment:
            known_paths = [path for path in lib_path_from_environment.split(separator)]  + self.known_paths
        else:
            known_paths = self.known_paths
        # expand ~
        known_paths = [os.path.expanduser(path) for path in known_paths]

        possible_libraries = [os.path.join(path, self._libname())
                              for path in known_paths]
        for library in possible_libraries:
            if os.path.exists(library):
                logger.info("Using model fortran library %s", library)
                return library
        msg = "Library not found, looked in %s" % ', '.join(possible_libraries)
        raise RuntimeError(msg)

    def _load_library(self):
        """Return the fortran library, loaded with """
        path = self._library_path()
        logger.info("Loading library from path {}".format(path))
        return cdll.LoadLibrary(path)

    def _annotate_functions(self):
        """Help ctypes by telling it type information about Fortran functions.

        Functions in the loaded Fortran library are called through  The
        variables inside Fortran don't automatically translate to and from
        Python variables. We can help ctypes a lot by telling it about the
        argument types and return type(s) of the various functions.

        The annotations also make our own life easier as it allows ctypes to
        do a lot of type conversions automatically for us. We can pass most
        values without the need to convert to a pointer first.

        On the wrapper.library the functions can be called as ctypes functions.
        On the wrapper the functions can be called with python types.

        """
        def wrap(func):
            """Return wrapped function with type conversion and sanity checks.
            """
            @functools.wraps(func, assigned=('restype', 'argtypes'))
            def wrapped(*args):
                if len(args) != len(func.argtypes):
                    logger.warn("{} {} not of same length",
                                args, func.argtypes)

                typed_args = []
                for (arg, argtype) in zip(args, func.argtypes):
                    if isinstance(argtype._type_, str):
                        # create a string buffer for strings
                        typed_arg = create_string_buffer(arg)
                    else:
                        # for other types, use the type to do the conversion
                        typed_arg = argtype(argtype._type_(arg))
                    typed_args.append(typed_arg)
                result = func(*typed_args)
                if hasattr(result, 'contents'):
                    return result.contents
                else:
                    return result
            return wrapped
        for function in FUNCTIONS:
            api_function = getattr(self.library, function['name'])
            api_function.argtypes = function['argtypes']
            api_function.restype = function['restype']
            # decorate the function with type conversion, so we can pass in
            # normal python stuff make sure the function properties are copied
            # to the wrapper (normally copy __doc__ etc...)
            # @functools.wraps(api_function,assigned=('restype','argtypes') )
            f = wrap(api_function)
            assert hasattr(f, 'argtypes')
            setattr(self, function['name'], f)

    def _load_model(self):
        os.chdir(os.path.dirname(self.configfile) or '.')
        logmsg = "Loading model {} in directory {}".format(
            self.configfile,
            os.path.abspath(os.getcwd())
        )
        logger.info(logmsg)
        exit_code = self.library.loadmodel(self.configfile.encode("utf-8"))
        if exit_code:
            errormsg = "Loading model {mdu} failed with exit code {code}"
            raise RuntimeError(errormsg.format(config=self.configfile, code=exit_code))

    def initialize(self):
        """Initialize and load the Fortran library (and model, if applicable).

        The Fortran library is loaded and ctypes is used to annotate functions
        inside the library. The Fortran library's initialization is called.

        Normally a path to an ``*.mdu`` model file is passed to the
        :meth:`__init__`. If so, that model is loaded. Note that
        :meth:`_load_model` changes the working directory to that of the model.

        """
        self.library = self._load_library()
        self._annotate_functions()
        self.library.initialize(self.configfile)  # Fortran init function.

    def finalize(self):
        """Shutdown the library and clean up the model.

        Note that the Fortran library's cleanup code is not up to snuff yet,
        so the cleanup is not perfect. Note also that the working directory is
        changed back to the original one.

        """
        if self.configfile:
            logger.info('finalize...')
            self.library.finalizemodel()
        logger.info('library shutdown...')
        logger.info('chdir...')
        # del self.library  # This one doesn't work.
        os.chdir(self.original_dir)

    # Variable Information Functions
    # Note that these call subroutines.
    # In python you expect a function to return something
    # In fortran subroutines can also return something in the input arguments
    # That's why we wrap these manually, we return the input arguments
    def get_var_type(self, name):
        """
        Return type string, compatible with numpy.
        """
        name = create_string_buffer(name)
        type_ = create_string_buffer(MAXSTRLEN)
        self.library.get_var_type.argtypes = [c_char_p, c_char_p]
        self.library.get_var_type(name, type_)
        return type_.value

    def inq_compound(self, name):
        """
        Return the number of fields and size (not yet) of a compound type.
        """
        name = create_string_buffer(name)
        self.library.inq_compound.argtypes = [c_char_p, POINTER(c_int)]
        self.library.inq_compound.restype = None
        nfields = c_int()
        self.library.inq_compound(name, byref(nfields))
        return nfields.value

    def inq_compound_field(self, name, index):
        """
        Lookup the type,rank and shape of a compound field
        """
        typename = create_string_buffer(name)
        index = c_int(index+1)
        fieldname = create_string_buffer(MAXSTRLEN)
        fieldtype = create_string_buffer(MAXSTRLEN)
        rank = c_int()
        arraytype = ndpointer(dtype='int32',
                              ndim=1,
                              shape=(MAXDIMS, ),
                              flags='F')
        shape = np.empty((MAXDIMS, ), dtype='int32', order='fortran')
        self.library.inq_compound_field.argtypes = [c_char_p,
                                                    POINTER(c_int),
                                                    c_char_p,
                                                    c_char_p,
                                                    POINTER(c_int),
                                                    arraytype]
        self.library.inq_compound_field.restype = None
        self.library.inq_compound_field(typename,
                                        byref(index),
                                        fieldname,
                                        fieldtype,
                                        byref(rank),
                                        shape)
        return (fieldname.value,
                fieldtype.value,
                rank.value,
                tuple(shape[:rank.value]))

    def make_compound_ctype(self, varname):
        """
        Create a ctypes type that corresponds to a compound type in memory.
        """

        # look up the type name
        compoundname = self.get_var_type(varname)
        nfields = self.inq_compound(compoundname)
        # for all the fields look up the type, rank and shape
        fields = []
        for i in range(nfields):
            (fieldname, fieldtype,
             fieldrank, fieldshape) = self.inq_compound_field(compoundname, i)
            assert fieldrank <= 1
            fieldctype = CTYPESMAP[fieldtype]
            if fieldrank == 1:
                fieldctype = fieldctype*fieldshape[0]
            fields.append((fieldname, fieldctype))
        # create a new structure

        class COMPOUND(Structure):
            _fields_ = fields

        # if we have a rank 1 array, create an array
        rank = self.get_var_rank(varname)
        assert rank <= 1, "we can't handle >=2 dimensional compounds yet"
        if rank == 1:
            shape = self.get_var_shape(varname)
            valtype = POINTER(ARRAY(COMPOUND, shape[0]))
        else:
            valtype = POINTER(COMPOUND)
        # return the custom type
        return valtype

    def get_var_rank(self, name):
        """
        Return array rank or 0 for scalar.
        """,
        name = create_string_buffer(name)
        rank = c_int()
        self.library.get_var_rank.argtypes = [c_char_p, POINTER(c_int)]
        self.library.get_var_rank.restype = None
        self.library.get_var_rank(name, byref(rank))
        return rank.value

    def get_var_shape(self, name):
        """
        Return shape of the array.
        """
        rank = self.get_var_rank(name)
        name = create_string_buffer(name)
        arraytype = ndpointer(dtype='int32',
                              ndim=1,
                              shape=(MAXDIMS, ),
                              flags='F')
        shape = np.empty((MAXDIMS, ), dtype='int32', order='fortran')
        self.library.get_var_shape.argtypes = [c_char_p, arraytype]
        self.library.get_var_shape(name, shape)
        return tuple(shape[:rank])

    # Change sliced to True, once we have a complete list of slices...
    def get_nd(self, name, sliced=False):
        """Return an nd array from model library"""
        if not name in DOCUMENTED_VARIABLES:
            # Enforcing documentation is really the only way to
            # ensure, well, documentation. Irritating, yes, but it
            # works. Document them in the ``DOCUMENTED_VARIABLES``
            # dictionary near the top of this Python file.
            msg = "Requesting variable '{}', but it isn't documented.".format(
                name)
            raise NotDocumentedError(msg)
        # How many dimensions.
        rank = self.get_var_rank(name)
        # The shape array is fixed size
        shape = np.empty((MAXDIMS, ), dtype='int32', order='fortran')
        shape = self.get_var_shape(name)
        # there should be nothing here...
        assert sum(shape[rank:]) == 0
        # variable type name
        type_ = self.get_var_type(name)

        is_numpytype = type_ in TYPEMAP

        if is_numpytype:
            # Store the data in this type
            arraytype = ndpointer(dtype=TYPEMAP[type_],
                                  ndim=rank,
                                  shape=shape,
                                  flags='F')
        else:
            arraytype = self.make_compound_ctype(name)
        # Create a pointer to the array type
        data = arraytype()
        # The functions get_var_type/_shape/_rank are already wrapped with
        # python function converter, get_var isn't.
        c_name = create_string_buffer(name)
        get_var = self.library.get_var
        get_var.argtypes = [c_char_p, POINTER(arraytype)]
        get_var.restype = None
        # Get the array
        get_var(c_name, byref(data))
        if not data:
            logger.info("NULL pointer returned")
            return None

        if is_numpytype:
            # array can be shared memory (always a copy)
            if self.sharedmem:
                shared_arr = multiprocessing.Array(
                    CTYPESMAP[TYPEMAP[type_]],
                    np.prod(shape), lock=True
                )
                array = np.frombuffer(shared_arr.get_obj())
                array[:] = np.array(data)
            # or a copy, if needed
            else:
                if name in NEED_COPYING:
                    logger.debug("copying %s, memory will be reallocated",
                                 name)
                    array = np.array(data).copy()
            # or just a pointer
                else:
                    array = np.ctypeslib.as_array(data)
        else:
            array = structs2pandas(data.contents)

        if name in SLICES and sliced:
            # return slice if needed
            array = array[SLICES[name]]
        return array

    def set_structure_field(self, name, id, field, value):
        # This only works for 1d
        rank = self.get_var_rank(name)
        assert rank == 1
        # The shape array is fixed size
        shape = np.empty((MAXDIMS, ), dtype='int32', order='fortran')
        shape = self.get_var_shape(name)
        # there should be nothing here...
        assert sum(shape[rank:]) == 0

        # look up the type name
        typename = self.get_var_type(name)
        assert typename not in TYPEMAP
        nfields = self.inq_compound(typename)
        # for all the fields look up the type, rank and shape
        fields = {}
        for i in range(nfields):
            (fieldname, fieldtype,
             fieldrank, fieldshape) = self.inq_compound_field(typename, i)
            assert fieldrank <= 1
            fieldctype = CTYPESMAP[fieldtype]
            if fieldrank == 1:
                fieldctype = fieldctype*fieldshape[0]
            fields[fieldname] = fieldctype

        T = fields[field]       # type (c_double)
        T_p = POINTER(T)        # void pointer, as used in the model

        set_structure_field = self.library.set_structure_field
        set_structure_field.argtypes = [
            c_char_p, c_char_p, c_char_p, POINTER(T_p)]
        set_structure_field.restype = None
        # So the value is a void pointer by reference....
        # Create a value wrapped in a c_double_p

        # wrap it up in the first pointer
        c_value = T_p(T(value))

        c_name = create_string_buffer(name)
        c_id = create_string_buffer(id)
        c_field = create_string_buffer(field)
        # Pass the void_p by reference...
        set_structure_field(c_name, c_id, c_field, byref(c_value))

    def __enter__(self):
        """Return the decorated instance upon entering the ``with`` block.

        We call the :meth:`start` method which starts everything up. Our
        return value is the Fortran library. This is what you get back from
        ``with ... as ...`` so that you can call Fortran functions on it.

        """
        self.initialize()
        return self

    def __exit__(self, type, value, tb):
        """Clean up what can be cleaned upon exiting the ``with`` block.

        We call the :meth:`stop` method that does the actual work.

        """
        self.finalize()
