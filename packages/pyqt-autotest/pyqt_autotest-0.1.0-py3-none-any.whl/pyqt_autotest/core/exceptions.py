# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from typing import List

from pyqt_autotest.results.exit_state import ExitState
from pyqt_autotest.results.results_logger import ResultsLogger
from pyqt_autotest.qt.top_level_widgets import clear_top_level_widgets, get_top_level_widget_classes

"""
Errors that occur due to invalid data or an setup being passed into pyqt-autotest.
"""


class SetupError(Exception):
    base_message: str = "An invalid widget setup has been detected, please correct the following:\n\n    "
    class_message: str = ""

    def report(self):
        messages = [self.base_message, self.class_message]
        print("".join(messages))
        ResultsLogger().save_buffer(ExitState.Error, messages)


class InheritanceError(SetupError):
    class_message: str = "The provided user class does not inherit from 'RandomAutoTest'."


class WidgetNotProvidedError(SetupError):
    class_message: str = "The provided user class does not implement a 'self.widget' member which is a QWidget."


class NoEnabledChildrenWidgetsError(SetupError):
    class_message: str = "The provided widget does not contain any children widgets which are enabled."


"""
Common errors that are found within a widget.
"""


class WidgetError(Exception):
    class_message: str = ""

    def report(self, messages: List[str]):
        print("".join(messages))

    def cleanup(self):
        pass


class CloseWidgetError(WidgetError):
    class_message: str = "Unexpected top level widget(s) detected after closing your widget:\n\n"

    def report(self):
        messages = [self.class_message, f"    {get_top_level_widget_classes()}\n"]
        ResultsLogger().save_buffer(ExitState.Warning, messages)
        super().report(messages)

    def cleanup(self):
        clear_top_level_widgets()
