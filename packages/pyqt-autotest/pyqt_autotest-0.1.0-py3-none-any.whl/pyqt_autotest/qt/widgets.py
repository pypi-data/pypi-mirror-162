# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from typing import List

from pyqt_autotest.core.exceptions import NoEnabledChildrenWidgetsError

from PyQt5.QtWidgets import QAbstractButton, QWidget


def get_widget_name(widget: QWidget) -> str:
    """Returns a string to represent the name of a widget. If a name can't be found, its className is returned."""
    if isinstance(widget, QAbstractButton) and widget.text().strip() != "":
        return widget.text()
    if widget.accessibleName() != "":
        return widget.accessibleName()
    if widget.objectName() != "":
        return widget.objectName()
    return widget.metaObject().className()


def find_child_widgets(parent_widget: QWidget, available_types: List[QWidget]) -> List[QWidget]:
    """Find the children widgets within the user's widget."""
    children_widgets = []
    for widget_type in available_types:
        children_widgets.extend(parent_widget.findChildren(widget_type))
    # Only return the widgets which are enabled
    enabled_widgets = [widget for widget in children_widgets if widget.isEnabled()]
    if len(enabled_widgets) == 0:
        raise NoEnabledChildrenWidgetsError()
    return enabled_widgets
