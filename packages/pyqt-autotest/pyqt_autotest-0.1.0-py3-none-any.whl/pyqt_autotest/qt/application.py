# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
import atexit
import sys
import traceback

from PyQt5.QtWidgets import QApplication
import sip

# Hold on to QAPP reference to avoid garbage collection
_QAPP = QApplication.instance()


@atexit.register
def cleanup_qapp_ref():
    """
    Remove the global reference to the QApplication object here
    """
    global _QAPP
    if _QAPP is not None:
        sip.delete(_QAPP)
    del _QAPP


def get_application(name=""):
    """
    Initialise and return the global application object
    :param name: Optional application name
    :return: Global appliction object
    """
    global _QAPP

    def exception_handler(exctype, value, tb):
        traceback.print_exception(exctype, value, tb)
        sys.exit(1)

    if _QAPP is None:
        _QAPP = QApplication([name])
        sys.excepthook = exception_handler

    return _QAPP
