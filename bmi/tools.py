#!/usr/bin/env python

"""
Run subgrid as a python script with colored output
"""
import argparse

from .wrapper import BMIWrapper

# do colorlogs here


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
    arguments = parse_args()
    # Read input file file
    with BMIWrapper(engine=arguments.engine, configfile=arguments.file) as model:
        t_end = model.get_end_time()
        t = 0
        while t < t_end:
            t = model.get_current_time()
            model.update(-1)
