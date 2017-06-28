import sys
import pkg_resources

if hasattr(sys, "frozen"):
    __version__ = '0.2.1'
else:
    __version__ = pkg_resources.get_distribution("bmi").version
