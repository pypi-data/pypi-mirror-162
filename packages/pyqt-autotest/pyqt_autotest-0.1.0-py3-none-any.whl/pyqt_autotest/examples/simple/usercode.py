import sys

from PyQt5.QtWidgets import QPushButton, QWidget


class UserWidget(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()

        self.success_button = QPushButton("Success", self)
        self.cause_exception_button = QPushButton("Cause Exception", self)
        self.cause_termination_button = QPushButton("Cause Termination", self)

        self.success_button.clicked.connect(self.successful_action)
        self.cause_exception_button.clicked.connect(self.cause_exception)
        self.cause_termination_button.clicked.connect(self.cause_termination)

    @staticmethod
    def successful_action():
        pass

    def cause_exception(self):
        raise RuntimeError("This is an exception in the users code.")

    @staticmethod
    def cause_termination():
        sys.exit(1)
