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
import os
import signal

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

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def trace(model):
    dirname = os.path.dirname(os.path.abspath(model.configfile))
    usage = get_size(dirname)
    info = dict(usage=usage)

    try:
        import psutil
        pid = os.getpid()
        process = psutil.Process(pid)
        memory = process.memory_info()._asdict()
        info.update(memory)
    except ImportError:
        # psutil not found, that's ok
        pass
    
    try:
        import pandas
        return pandas.Series(info)
    except ImportError:
        # pandas not found, that's ok
        return info


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
        # if siginfo is supported by OS (BSD)
        def handler(signum, frame):
            """report progress information"""
            t_start = model.get_start_time()
            t_end = model.get_end_time()
            t_current = model.get_current_time()
            total = (t_end - t_start)
            now = (t_current - t_start)
            if total > 0:
                logging.info("progress: %s%%", 100.0 * now / total)
            else:
                logging.info("progress: unknown")

        if hasattr(signal, 'SIGINFO'):
            # attach a siginfo handler (CTRL-t) to print progress
            signal.signal(signal.SIGINFO, handler)

        if arguments['--info']:
            logging.info("%s", trace(model))
        t_end = model.get_end_time()
        t = model.get_start_time()
        while t < t_end:
            model.update(-1)
            t = model.get_current_time()
        if arguments['--info']:
            logging.info("%s", trace(model))

if __name__ == '__main__':
    main()
