# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from typing import List

from pyqt_autotest.core.auto_test import _AutoTest
from pyqt_autotest.qt.widgets import find_child_widgets, get_widget_name
from pyqt_autotest.utilities.randomizer import get_random_action, get_random_widget

from PyQt5.QtWidgets import QWidget


class RandomAutoTest(_AutoTest):
    """
    An auto test class for performing random actions on random widgets within a user widget.
    """

    def _perform_action_arguments(self):
        """Returns the arguments to be used when performing an action."""
        return [find_child_widgets(self.widget, list(self.options.widget_actions.keys()))]

    def _perform_action(self, _: int, all_widgets: List[QWidget]) -> None:
        """Performs a random action on a random widget."""
        widget = get_random_widget(all_widgets)
        action_name = get_random_action(type(widget), self.options.widget_actions)
        self._logger.record_event(get_widget_name(widget), str(action_name))
        # Perform action on a child widget
        self.options.actions[action_name](widget)
