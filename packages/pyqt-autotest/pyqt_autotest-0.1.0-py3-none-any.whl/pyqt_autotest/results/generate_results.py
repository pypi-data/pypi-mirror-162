# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader
from os import getcwd
from os.path import abspath, dirname, join
from typing import List

from pyqt_autotest.results.event_list import EventList
from pyqt_autotest.results.exit_state import ExitState
from pyqt_autotest.results.results_logger import ResultsLogger

CSS_FILENAME = "style.css"
INDEX_FILENAME = "index.html"
INSTRUCTIONS_FILENAME = "instructions.html"
JS_FILENAME = "autotest.js"
STATIC_DIRECTORY = "static"
TEMPLATE_DIRECTORY = "templates"


def _generate_index_page(template, css_style_sheet: str, run_links: List[str], output_directory: str) -> str:
    """Generate a html page which functions as an index page."""
    index_html = join(output_directory, INDEX_FILENAME)

    with open(index_html, "w") as file:
        results_logger = ResultsLogger()

        file.write(template.render(
            css_style_sheet=css_style_sheet,
            number_of_successes=results_logger.count_exit_state(ExitState.Success),
            number_of_warnings=results_logger.count_exit_state(ExitState.Warning),
            number_of_errors=results_logger.count_exit_state(ExitState.Error),
            run_list=list(zip(results_logger.runs(), run_links))))

    return index_html


def _generate_run_instructions_page(template, event_list: EventList, css_style_sheet: str, js_file: str,
                                    output_directory: str) -> str:
    """Generates a html page for displaying repeatable instructions."""
    instructions_html = join(output_directory, f"{event_list.title.lower().replace(' ', '_')}_instructions.html")

    with open(instructions_html, "w") as file:
        file.write(template.render(
            css_style_sheet=css_style_sheet,
            js_file=js_file,
            event_list=event_list))

    return instructions_html


def generate_html_results(output_directory: str) -> str:
    """
    Generates the results from running PyQtAutoTest into html files.
    @param output_directory: The relative directory to store the resulting html files in.
    @returns An absolute path to the generated results index page.
    """
    results_directory = dirname(abspath(__file__))
    static_directory = join(results_directory, STATIC_DIRECTORY)
    template_directory = join(results_directory, TEMPLATE_DIRECTORY)
    template_loader = Environment(loader=FileSystemLoader(template_directory))
    index_template = template_loader.get_template(INDEX_FILENAME)
    instructions_template = template_loader.get_template(INSTRUCTIONS_FILENAME)

    output_directory = join(getcwd(), output_directory)
    css_style_sheet = join(output_directory, STATIC_DIRECTORY, CSS_FILENAME)
    js_file = join(output_directory, STATIC_DIRECTORY, JS_FILENAME)

    # Creates output_directory if it doesn't exist, and copies static directory
    copy_tree(static_directory, join(output_directory, STATIC_DIRECTORY))

    run_instruction_links = [_generate_run_instructions_page(instructions_template, run, css_style_sheet, js_file,
                                                             output_directory)
                             for run in ResultsLogger().runs()]

    return _generate_index_page(index_template, css_style_sheet, run_instruction_links, output_directory)
