from transcriber.transcriber import Transcriber

from pyqt_autotest.core.action import Action
from pyqt_autotest.random_auto_test import RandomAutoTest

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QCheckBox, QLineEdit, QSpinBox


class ComplexRandomTest(RandomAutoTest):

    def setup_options(self):
        extra_actions = {
            "Key text": lambda widget: QTest.keyClicks(widget, "dummy text"),
            "Left click in centre": lambda widget: QTest.mouseClick(widget, Qt.LeftButton,
                                                                    pos=QPoint(2, widget.height() / 2))
        }
        extra_widget_actions = {
            QCheckBox: ["Left click in centre"],
            QLineEdit: ["Key text"],
            QSpinBox: [Action.KeyDownClick, Action.KeyUpClick]
        }

        self.options.actions.update(extra_actions)
        self.options.widget_actions.update(extra_widget_actions)

        self.options.number_of_runs = 1
        self.options.number_of_actions = 10
        self.options.wait_time = 300  # milliseconds
        self.options.output_directory = "complex_results"

    def setup_widget(self):
        # Must instantiate the 'self.widget' member variable, and it must be a QWidget
        self.widget = Transcriber()

        # TODO It would be even better to load data before the test begins
