# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from random import randint
from typing import Dict, List, Tuple

from pyqt_autotest.core.action import Action

from PyQt5.QtWidgets import QWidget


def get_random_widget(widgets: List[Tuple[str, type]]) -> Tuple[str, str]:
    """Get a random widget and its type."""
    number_of_widgets = len(widgets)
    if number_of_widgets > 0:
        return widgets[randint(0, number_of_widgets - 1)]
    else:
        raise RuntimeError("Failed to find any child widgets within your widget.")


def get_random_action(widget_type: type, widget_actions: Dict[QWidget, List[Action]]) -> str:
    """Get a random action to perform on a specific widget type."""
    actions_for_widget = widget_actions.get(widget_type, [])
    number_of_actions = len(actions_for_widget)
    if number_of_actions == 0:
        raise RuntimeError(f"Failed to find any actions for a widget of type {widget_type}.")

    return actions_for_widget[randint(0, number_of_actions - 1)]
