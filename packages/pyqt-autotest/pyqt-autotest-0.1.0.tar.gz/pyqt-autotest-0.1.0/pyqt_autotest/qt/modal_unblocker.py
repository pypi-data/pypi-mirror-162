# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QApplication, QFileDialog

WINDOW_BLOCKED_CODE = 103


class WindowUnblockFilter(QObject):
    """
    An event filter class to close any modal widgets which are blocking further processing.
    """

    def eventFilter(self, obj,  event):
        # QEvent::WindowBlocked - The window is blocked by a modal dialog
        if event.type() == WINDOW_BLOCKED_CODE:
            close_modals_if_exist(QFileDialog)

        return super().eventFilter(obj, event)


def close_modals_if_exist(widget_type: type) -> None:
    """Close any top level widgets that are blocking further actions, and have a specific widget type."""
    for widget in QApplication.topLevelWidgets():
        if widget.windowModality() == 2 and isinstance(widget, widget_type):
            widget.setAttribute(Qt.WA_DeleteOnClose)
            widget.close()
