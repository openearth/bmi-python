#!/usr/bin/env python
"""
Run a BMI model

Usage:
    bmi-runner <engine> [<config>] [--disable-logger] [--info]
    bmi-runner -h | --help

Positional arguments:
    engine      model engine name, this is either name of the library (e.g. model1) or full path to the BMI library (/usr/lib/libmodel1.so.5 or C:\\opt\\model1.dll)
    config      model config file, used to initialize model

Options:
    -h, --help        show this help message and exit
    --disable-logger  do not inject logger into the BMI library
    --info            display information about the model
"""
import logging

import docopt

from .wrapper import BMIWrapper
from . import __version__


# do colorlogs here
def colorlogs(format="short"):
    """Append a rainbow logging handler and a formatter to the root logger"""
    try:
        from rainbow_logging_handler import RainbowLoggingHandler
        import sys
        # setup `RainbowLoggingHandler`
        logger = logging.root
        # same as default
        if format == "short":
            fmt = "%(message)s "
        else:
            fmt = "[%(asctime)s] %(name)s %(funcName)s():%(lineno)d\t%(message)s [%(levelname)s]"
        formatter = logging.Formatter(fmt)
        handler = RainbowLoggingHandler(sys.stderr,
                                        color_funcName=('black', 'gray', True))
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except ImportError:
        # rainbow logger not found, that's ok
        pass

def info(model):
    n = model.get_var_count()
    logging.info("variables (%s):", n)
    for i in range(n):
        name = model.get_var_name(i)
        rank = model.get_var_rank(name)
        type = model.get_var_type(name)
        shape = model.get_var_shape(name)
        vartxt = "%s" % (model.get_var(name), )
        msg = "{name} ({rank}D, {shape}, {type}):\n{vartxt}"
        logging.debug(msg.format(**locals()))


def main():
    """main bmi runner program"""
    arguments = docopt.docopt(__doc__, version=__version__)
    colorlogs()
    # Read input file file
    wrapper = BMIWrapper(
        engine=arguments['<engine>'],
        configfile=arguments['<config>'] or ''
    )
    # add logger if required
    if not arguments['--disable-logger']:
        logging.root.setLevel(logging.DEBUG)
        wrapper.set_logger(logging.root)
    with wrapper as model:
        if arguments['--info']:
            info(model)
        t_end = model.get_end_time()
        t = model.get_start_time()
        while t < t_end:
            t = model.get_current_time()
            model.update(-1)


if __name__ == '__main__':
    main()
