# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from pyqt_autotest.cli.options import (DEFAULT_NUMBER_OF_RUNS, DEFAULT_NUMBER_OF_ACTIONS, DEFAULT_WAIT_TIME,
                                       DEFAULT_OUTPUT_DIRECTORY)
from pyqt_autotest.cli.run import run

import argparse
import sys


def get_parser():
    """
    Create and return a parser for capturing the command line arguments.
    :return: configured argument parser
    :rtype: argparse.ArgParser
    """

    epilog = """
Usage Examples:

    $ autotest -t pyqt_autotest.examples.simple.test.SimpleAutoTest
    $ autotest -t pyqt_autotest.examples.simple.test.SimpleAutoTest -r 5 -a 10 -w 500 -o autotest_results

For more information on this package, please see the documentation pages found in the pyqt-autotest Github repository.
"""

    parser = argparse.ArgumentParser(
        prog="PyQtAutoTest", add_help=True, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-t", "--test-class", required=True,
                        help="A module path to a python class which inherits from RandomAutoTest.")

    parser.add_argument("-r", "--number-of-runs",
                        metavar="NUMBER_OF_RUNS",
                        help=f"The number of times to open the widget and perform a random selection of actions. "
                             f"(Default = {DEFAULT_NUMBER_OF_RUNS})")
    parser.add_argument("-a", '--number-of-actions',
                        metavar="NUMBER_OF_ACTIONS",
                        help=f"The number of random actions to perform each time the widget is opened. "
                             f"(Default = {DEFAULT_NUMBER_OF_ACTIONS})")
    parser.add_argument("-w", "--wait-time",
                        metavar="WAIT_TIME",
                        help=f"The number of milliseconds to wait between executing two consecutive actions. "
                             f"(Default = {DEFAULT_WAIT_TIME})")
    parser.add_argument("-o", "--output-directory",
                        metavar="OUTPUT_DIRECTORY",
                        help=f"The relative directory to store the output files in. "
                             f"(Default = '{DEFAULT_OUTPUT_DIRECTORY}')")
    return parser


def main():
    """
    Entry point to be exposed as the `pyqt_autotest` command.
    """
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    output_directory = args.output_directory if args.output_directory is not None else ""

    run(args.test_class,
        number_of_runs=args.number_of_runs,
        number_of_actions=args.number_of_actions,
        wait_time=args.wait_time,
        output_directory=output_directory)
