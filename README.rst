Python wrapper for BMI models
==========================================

This is ctypes wrapper for BMI models.

The BMI_ describes a low level interface for numerical models.

.. image:: https://travis-ci.org/openearth/bmi-python.svg?branch=master
    :target: https://travis-ci.org/openearth/bmi-python
    
Origin
------
This module is based on code from:

- CSMDS: https://csdms.colorado.edu/svn/bmi/trunk/python/bmi/BMI.py
- OpenEarth: http://svn.oss.deltares.nl/repos/openearthtools/trunk/python/OpenEarthTools
- 3Di: https://github.com/nens/python-subgrid

Models
------
Several models implement the BMI_ interface.

- Subgrid: https://github.com/nens/python-subgrid
- Swan: https://github.com/SiggyF/chenopis
- XBeach: http://svn.oss.deltares.nl/repos/xbeach
- DFlow-FM: https://repos.deltares.nl/repos/ds/trunk/additional/unstruc/python/dflowfm

Prerequisites
-------------

We need a compiled BMI library (dll, so, dylib). There are a couple of common
locations where we look for it.::

   .
   ~/local/lib
   ~/.local/lib
   /opt/modelname/lib
   /usr/local/lib
   /usr/lib

A convention on linux is to install the library into ``/opt/modelname/``.
If you are using one of the models above, the modelname will be  3di, dflowfm, xbeach or swan

In case you have an alternative location, you can set the ``LD_LIBRARY_PATH``, (``DYLD_LIBRARY_PATH`` in OSX, ``PATH`` in windows)
environment variable, for example for 3Di::

   $ export LD_LIBRARY_PATH=/home/user/svn/3di/trunk/subgridf90/src/.libs

(On windows the command is ``set`` instead of ``export``).

Setup
------

The virtualenv way (assumes virtualenvwrapper and virtualenv are installed)::

  mkvirtualenv main
  workon main
  # get the version from pypi
  pip install bmi
  # or if you want to add your source directory to the path
  pip install -e .

Combination Windows and Anaconda::

- Download + Install Anaconda
- Download and install the :faulthandler: package, from http://www.lfd.uci.edu/~gohlke/pythonlibs/#faulthandler
- Download and install the :NetCDF4: package, from http://www.lfd.uci.edu/~gohlke/pythonlibs/#netcdf4
- Open an (Anaconda) Python-terminal (Press :[Ctrl]:+:[Alt]+:A:).
- pip.bat install -e ``<path to your bmi-python GIT working copy>``


Usage
-----

There are two ways to use the wrapper. A handy way is as a context
manager, so with a ``with`` statement::

    with BMIWrapper(engine="model", configfile='/full/path/model.ini') as model:
        # model is the actual library.
        model.something()

The second way is by calling :meth:`start` and :meth:`stop` yourself and
using the :attr:`library` attribute to access the Fortran library::

    wrapper = BMIWrapper(engine="model", configfile='/full/path/model.mdu')
    wrapper.start()
    wrapper.library.something()
    ...
    wrapper.stop()

Note: Without the ``mdu`` argument, no model is loaded and you're free to
use the library as you want.


Convenience scripts
-------------------

The python bmi library contains a script that can be used as a command line runner for your model::

  bmi-runner <engine> <configfile>

Links
--------
.. _BMI: http://csdms.colorado.edu/wiki/BMI_Description
