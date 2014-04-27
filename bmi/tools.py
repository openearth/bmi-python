#!/usr/bin/env python

"""
Run subgrid as a python script with colored output
"""
import argparse
import logging

from .wrapper import BMIWrapper


# do colorlogs here
def colorlogs():
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


def parse_args():
    """
    Parse the command line arguments
    """
    argumentparser = argparse.ArgumentParser(
        description='Run a BMI model')
    argumentparser.add_argument('engine', help='model engine')
    argumentparser.add_argument('file', help='input file')
    arguments = argumentparser.parse_args()
    return arguments


def runner():
    """main program"""
    colorlogs()
    arguments = parse_args()
    # Read input file file
    wrapper = BMIWrapper(engine=arguments.engine, configfile=arguments.file)
    logging.root.setLevel(logging.DEBUG)
    wrapper.set_logger(logging.root)
    with wrapper as model:
        t_end = model.get_end_time()
        t = 0
        while t < t_end:
            t = model.get_current_time()
            model.update(-1)
