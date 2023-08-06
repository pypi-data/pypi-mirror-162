# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from copy import copy
from typing import List

from pyqt_autotest.results.event_list import EventList
from pyqt_autotest.results.exit_state import ExitState
from pyqt_autotest.utilities.singleton import Singleton


class ResultsLogger(metaclass=Singleton):
    """
    A class to log the actions that are tested and whether there is a warning/error.
    """
    _runs: List[EventList] = []
    _event_buffer: EventList = EventList()

    def is_buffer_empty(self) -> bool:
        """Returns true if the buffer is empty i.e. A test isn't being run."""
        return len(self._event_buffer) == 0

    def save_buffer(self, exit_state: ExitState, message: List[str] = None) -> None:
        """Save the event buffer when a test run ends."""
        self._event_buffer.title = f"Run {len(self._runs) + 1}"
        self._event_buffer.set_exit_state(exit_state, message)
        self._runs.append(copy(self._event_buffer))
        self._event_buffer.clear()

    def record_event(self, widget_name: str, event_name: str) -> None:
        """Record an event in the event buffer."""
        self._event_buffer.add_event(widget_name, event_name)

    def runs(self) -> List[EventList]:
        """Returns the runs recorded in the results logger."""
        return self._runs

    def count_exit_state(self, exit_state: ExitState) -> int:
        """Count the number of runs with a particular exit state."""
        return len([run for run in self._runs if run.exit_state == exit_state])
