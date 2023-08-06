from os.path import abspath, dirname, join

from n_body_simulations.qt.model import NBodySimulationsModel
from n_body_simulations.qt.presenter import NBodySimulationsPresenter
from n_body_simulations.qt.view import NBodySimulationsView

from pyqt_autotest.random_auto_test import RandomAutoTest

FILENAME = "three-body-parameters.txt"


class ModerateRandomTest(RandomAutoTest):

    def setup_options(self):
        self.options.number_of_runs = 2
        self.options.number_of_actions = 10
        self.options.wait_time = 1000  # milliseconds
        self.options.output_directory = "moderate_results"

    def setup_widget(self):
        # Must instantiate the 'self.widget' member variable, and it must be a QWidget
        self.widget = NBodySimulationsView()

        self.model = NBodySimulationsModel()
        self.presenter = NBodySimulationsPresenter(self.widget, self.model)

        # Load a project file into the widget to make the testing more interesting
        project_file = join(dirname(abspath(__file__)), FILENAME)
        self.presenter._load_project(project_file)
