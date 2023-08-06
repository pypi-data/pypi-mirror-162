# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from os.path import dirname, realpath

from pyqt_autotest.core.exception_handler import catch_exceptions
from pyqt_autotest.qt.application import get_application

app = get_application()


@catch_exceptions
def run(module_and_class: str, number_of_runs: int, number_of_actions: int, wait_time: int, output_directory: str):
    global app

    with open(f"{dirname(realpath(__file__))}/run_test.py.in") as file:
        template_code = file.read()

    if template_code != "":
        module_split = module_and_class.split(".")
        module, class_name = ".".join(module_split[:-1]), module_split[-1]
        exec(template_code.format(module, class_name, number_of_runs, number_of_actions, wait_time, output_directory))
