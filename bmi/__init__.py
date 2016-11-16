import pkg_resources,sys

if hasattr(sys, "frozen"):
    __version__ = '0.1'
else:
    __version__ = pkg_resources.get_distribution("bmi").version
