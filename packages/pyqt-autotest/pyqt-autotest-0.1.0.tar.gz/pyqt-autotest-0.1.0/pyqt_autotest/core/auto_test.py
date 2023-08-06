# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
import sys
from abc import ABCMeta, abstractmethod

from pyqt_autotest.cli.options import Options
from pyqt_autotest.core.exception_handler import (catch_exceptions, exception_hook, exit_hook,
                                                  unraisable_exception_hook)
from pyqt_autotest.core.exceptions import CloseWidgetError, WidgetNotProvidedError
from pyqt_autotest.results.generate_results import generate_html_results
from pyqt_autotest.results.open_results import open_browser
from pyqt_autotest.results.results_logger import ResultsLogger
from pyqt_autotest.results.exit_state import ExitState
from pyqt_autotest.qt.modal_unblocker import close_modals_if_exist, WindowUnblockFilter
from pyqt_autotest.qt.top_level_widgets import get_top_level_widget_classes

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtTest import QTest
from tqdm import tqdm


class _AutoTest(metaclass=ABCMeta):

    def __init__(self, options: Options):
        super(_AutoTest, self).__init__()
        self.widget: QWidget = None
        self.options: Options = options

        self._logger = ResultsLogger()

        # Used to unblock the main widget if a modal QFileDialog opens and blocks further actions
        self.modal_unblocker = WindowUnblockFilter()

        sys.exit = exit_hook
        sys.excepthook = exception_hook
        sys.unraisablehook = unraisable_exception_hook

    def setup_options(self) -> None:
        """The method used to set the options for the test (optional)."""
        pass

    @abstractmethod
    def setup_widget(self) -> None:
        """The method used to instantiate the users widget."""
        pass

    @catch_exceptions
    def _run(self) -> None:
        """Runs the random widget testing."""
        self.setup_options()
        for run_number in range(1, self.options.number_of_runs + 1):
            self._run_actions(run_number)

        open_browser(generate_html_results(self.options.output_directory))

    @catch_exceptions
    def _run_actions(self, run_number: int) -> None:
        """Sets up the widget and runs the actions for a single run."""
        self.setup_widget()
        if not isinstance(self.widget, QWidget):
            raise WidgetNotProvidedError()
        self.widget.setAttribute(Qt.WA_DeleteOnClose)
        self.widget.installEventFilter(self.modal_unblocker)
        self.widget.show()

        arguments = self._perform_action_arguments()
        for action_number in tqdm(range(self.options.number_of_actions),
                                  desc=f"Running... ({run_number}/{self.options.number_of_runs})",
                                  bar_format="{l_bar}{bar}|", ncols=80):
            # After a certain timeout, attempt to close any QMessageBox's that could be blocking the main widget
            QTimer.singleShot(2 * self.options.wait_time, lambda: close_modals_if_exist(QMessageBox))
            self._perform_action(action_number, *arguments)
            # Wait for a given number of milliseconds
            QTest.qWait(self.options.wait_time)
            if self._logger.is_buffer_empty():
                break
        self._close_widget()

    @abstractmethod
    def _perform_action_arguments(self):
        """Returns the arguments to be used when performing an action."""
        pass

    @abstractmethod
    def _perform_action(self, *args) -> None:
        """Performs an action on a widget."""
        pass

    @catch_exceptions
    def _close_widget(self) -> None:
        """Closes the widget and starts the event loop to ensure all events are processed."""
        self.widget.close()
        self.widget = None
        QTest.qWait(self.options.wait_time)

        if not self._logger.is_buffer_empty():
            if len(get_top_level_widget_classes()) == 0:
                self._logger.save_buffer(ExitState.Success)
            else:
                raise CloseWidgetError()
