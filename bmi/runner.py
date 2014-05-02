#!/usr/bin/env python
"""
Run a BMI model

Usage:
    bmi-runner <engine> <config>

Positional arguments:
    engine      model engine name, this is either name of the library (e.g. model1) or full path to the BMI library (/usr/lib/libmodel1.so.5 or C:\opt\model1.dll)
    config      model config file, used to initialize model

Options:
    -h, --help  show this help message and exit
"""
import docopt
import logging

from .wrapper import BMIWrapper
from . import __version__


# do colorlogs here
def colorlogs():
    """Append a rainbow logging handler and a formatter to the root logger"""
    try:
        from rainbow_logging_handler import RainbowLoggingHandler
        import sys
        # setup `RainbowLoggingHandler`
        logger = logging.root
        # same as default
        format = "[%(asctime)s] %(name)s %(funcName)s():%(lineno)d\t%(message)s [%(levelname)s]"
        formatter = logging.Formatter(format)
        handler = RainbowLoggingHandler(sys.stderr,
                                        color_funcName=('black', 'gray', True))
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except ImportError:
        # rainbow logger not found, that's ok
        pass


def main():
    """main bmi runner program"""
    arguments = docopt.docopt(__doc__, version=__version__)
    colorlogs()
    # Read input file file
    wrapper = BMIWrapper(engine=arguments['<engine>'], configfile=arguments['<config>'])
    logging.root.setLevel(logging.DEBUG)
    wrapper.set_logger(logging.root)
    with wrapper as model:
        t_end = model.get_end_time()
        t = 0
        while t < t_end:
            t = model.get_current_time()
            model.update(-1)

if __name__ == '__main__':
    main()
