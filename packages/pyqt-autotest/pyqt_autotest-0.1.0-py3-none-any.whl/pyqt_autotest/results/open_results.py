# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from os.path import relpath
from platform import system
from webbrowser import open_new

from pyqt_autotest.results.exit_state import ExitState
from pyqt_autotest.results.results_logger import ResultsLogger
from pyqt_autotest.utilities.print_colors import PrintColors


def open_browser(output_file: str) -> None:
    """
    Opens a browser window to show the results from running PyQtAutoTest.
    @param output_file: The absolute path to the generated results index page.
    """
    # Use the relative path so that the browser can open on Mac and WSL
    relative_path = relpath(output_file)
    # Construct a url that can be pasted into a browser
    is_mac = system() == "Darwin"
    url = "file://" + output_file if is_mac else output_file

    if open_new(url if is_mac else relative_path):
        results_logger = ResultsLogger()
        number_of_successes = results_logger.count_exit_state(ExitState.Success)
        number_of_warnings = results_logger.count_exit_state(ExitState.Warning)
        number_of_errors = results_logger.count_exit_state(ExitState.Error)

        print(f"\nPyQt AutoTest results have been successfully opened in your browser from this url:\n\n    {url}\n"
              f"\nSuccesses ({PrintColors.SUCCESS}{number_of_successes}{PrintColors.END}) | "
              f"Warnings ({PrintColors.WARNING}{number_of_warnings}{PrintColors.END}) | "
              f"Errors ({PrintColors.ERROR}{number_of_errors}{PrintColors.END})\n")
    else:
        print(f"\nWARNING:\n  Failed to open browser. Please copy and paste this url into your browser:\n\n   {url}\n")
