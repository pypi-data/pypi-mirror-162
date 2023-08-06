from pyqt_autotest.examples.simple.usercode import UserWidget
from pyqt_autotest.random_auto_test import RandomAutoTest


class SimpleRandomTest(RandomAutoTest):

    def setup_options(self):
        self.options.number_of_runs = 4
        self.options.number_of_actions = 4
        self.options.wait_time = 200  # milliseconds
        self.options.output_directory = "simple_results"

    def setup_widget(self):
        # Must instantiate the 'self.widget' member variable, and it must be a QWidget
        self.widget = UserWidget()
