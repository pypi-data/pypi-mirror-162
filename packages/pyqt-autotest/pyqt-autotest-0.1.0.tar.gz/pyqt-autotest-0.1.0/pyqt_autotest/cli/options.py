# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from typing import Callable, Dict

from pyqt_autotest.core.action import Action

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QPushButton

DEFAULT_NUMBER_OF_RUNS = 1
DEFAULT_NUMBER_OF_ACTIONS = 10
DEFAULT_WAIT_TIME = 50
DEFAULT_OUTPUT_DIRECTORY = "autotest_results"


class Options:
    actions: Dict[Action, Callable] = {
        Action.KeyDownClick: lambda widget: QTest.keyClick(widget, Qt.Key_Down),
        Action.KeyUpClick: lambda widget: QTest.keyClick(widget, Qt.Key_Up),
        Action.MouseLeftClick: lambda widget: QTest.mouseClick(widget, Qt.LeftButton)
    }

    widget_actions = {
        QPushButton: [Action.MouseLeftClick]
    }

    def __init__(self, number_of_runs: int = None, number_of_actions: int = None, wait_time: int = None,
                 output_directory: str = ""):
        self._number_of_runs: int = number_of_runs
        self._number_of_actions: int = number_of_actions
        self._wait_time: int = wait_time
        self._output_directory: str = output_directory

    @property
    def number_of_runs(self) -> int:
        """Returns the number_of_runs option, or a default if it hasn't been set."""
        if self._number_of_runs is None:
            return DEFAULT_NUMBER_OF_RUNS
        return self._number_of_runs

    @number_of_runs.setter
    def number_of_runs(self, n_runs: int) -> None:
        """Sets the number_of_runs option if it hasn't already been provided on the command line."""
        if n_runs is None:
            return
        if not isinstance(n_runs, int):
            raise ValueError("The provided 'number_of_runs' option is not an int.")

        if self._number_of_runs is None:
            self._number_of_runs = n_runs

    @property
    def number_of_actions(self) -> int:
        """Returns the number_of_actions option, or a default if it hasn't been set."""
        if self._number_of_actions is None:
            return DEFAULT_NUMBER_OF_ACTIONS
        return self._number_of_actions

    @number_of_actions.setter
    def number_of_actions(self, n_actions: int) -> None:
        """Sets the number_of_actions option if it hasn't already been provided on the command line."""
        if n_actions is None:
            return
        if not isinstance(n_actions, int):
            raise ValueError("The provided 'number_of_actions' option is not an int.")

        if self._number_of_actions is None:
            self._number_of_actions = n_actions

    @property
    def wait_time(self) -> int:
        """Returns the wait_time option, or a default if it hasn't been set."""
        if self._wait_time is None:
            return DEFAULT_WAIT_TIME
        return self._wait_time

    @wait_time.setter
    def wait_time(self, wait_time: int) -> None:
        """Sets the wait_time option if it hasn't already been provided on the command line."""
        if wait_time is None:
            return
        if not isinstance(wait_time, int):
            raise ValueError("The provided 'wait_time' option is not an int.")

        if self._wait_time is None:
            self._wait_time = wait_time

    @property
    def output_directory(self) -> str:
        """Returns the output_directory option, or a default if it hasn't been set."""
        if self._output_directory == "":
            return DEFAULT_OUTPUT_DIRECTORY
        return self._output_directory

    @output_directory.setter
    def output_directory(self, output_directory: str) -> None:
        """Sets the output_directory option if it hasn't already been provided on the command line."""
        if output_directory == "":
            return
        if not isinstance(output_directory, str):
            raise ValueError("The provided 'output_directory' option is not a string.")

        if self._output_directory == "":
            self._output_directory = output_directory
