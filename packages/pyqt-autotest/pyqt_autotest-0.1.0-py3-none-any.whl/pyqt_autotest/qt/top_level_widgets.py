# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

EXCLUDE_TOP_LEVEL_CLASSES = ["QComboBoxPrivateContainer"]


def get_top_level_widget_classes() -> List[str]:
    """Returns a list of top level widget class names."""
    top_level_widget_classes = []
    for widget in QApplication.topLevelWidgets():
        class_name = widget.metaObject().className()
        if class_name not in EXCLUDE_TOP_LEVEL_CLASSES:
            top_level_widget_classes.append(class_name)
    return top_level_widget_classes


def clear_top_level_widgets() -> None:
    """Close and delete all existing top level widgets."""
    for widget in QApplication.topLevelWidgets():
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.close()
