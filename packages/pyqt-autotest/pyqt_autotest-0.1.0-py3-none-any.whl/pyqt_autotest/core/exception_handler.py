# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from functools import wraps
from sys import exc_info
from traceback import format_exception

from pyqt_autotest.core.exceptions import SetupError, WidgetError
from pyqt_autotest.results.exit_state import ExitState
from pyqt_autotest.results.results_logger import ResultsLogger


def exit_hook(args):
    """Used to hook a system exit and report the system exit."""
    message_list = [f"A SystemExit exception was raised with arguments: {str(args)}\n"]
    print("\n" + "".join(message_list))
    ResultsLogger().save_buffer(ExitState.Error, message_list)


def exception_hook(type, exception, traceback):
    """Used to hook an exception and report the exception."""
    message_list = format_exception(type, exception, traceback)
    print("\n" + "".join(message_list))
    ResultsLogger().save_buffer(ExitState.Error, message_list)


def unraisable_exception_hook(unraisable):
    """Used to hook an unraisable exception and report the unraisable exception."""
    message_list = format_exception(*exc_info())
    print("\n" + "".join(message_list))
    ResultsLogger().save_buffer(ExitState.Error, message_list)


def catch_exceptions(function):
    """A decorator function used to catch exceptions in a function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except SetupError as ex:
            ex.report()
        except WidgetError as ex:
            ex.report()
            ex.cleanup()
        except BaseException as ex:
            print("\n" + str(ex))
            ResultsLogger().save_buffer(ExitState.Error, format_exception(*exc_info()))

    return wrapper
