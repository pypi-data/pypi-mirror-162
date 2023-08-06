# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from typing import List, Tuple

from pyqt_autotest.results.exit_state import ExitState

BACKGROUND_CLASS = {
    ExitState.Error: "background-error",
    ExitState.Warning: "background-warning",
    ExitState.Success: "background-success"
}
COLOR_CLASS = {
    ExitState.Error: "color-error",
    ExitState.Warning: "color-warning",
    ExitState.Success: "color-success"
}
ICON_CLASS = {
    ExitState.Error: "color-error fa-solid fa-circle-xmark",
    ExitState.Warning: "color-warning fa-solid fa-circle-exclamation",
    ExitState.Success: "color-success fa-solid fa-circle-check"
}
MAX_BRIEF_MESSAGE_LENGTH = 100
SUCCESS_MESSAGE = "This was a successful run"


class EventList:

    def __init__(self):
        self._events: List[Tuple[str, str]] = []
        self._title: str = ""
        self._message: List[str] = []
        self._exit_state: ExitState = None

    def __len__(self) -> int:
        """Returns the length of the event list."""
        return len(self._events)

    @property
    def title(self) -> str:
        """Returns the title to use for this event list."""
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        """Sets the title to use for this event list."""
        self._title = title

    @property
    def message(self) -> str:
        """Returns the full success, warning or error message."""
        if len(self._message) != 0:
            return "".join(self._message).replace("\n", "<br>").replace(" ", "&nbsp;")
        return SUCCESS_MESSAGE

    @property
    def brief_message(self) -> str:
        """Returns a brief message to accompany the title on the index page."""
        if len(self._message) != 0:
            return self._message[0][:min(MAX_BRIEF_MESSAGE_LENGTH, len(self.message))] + "..."
        return SUCCESS_MESSAGE

    @property
    def icon_class(self) -> str:
        """Returns the icon class to use for the particular exit state."""
        return ICON_CLASS.get(self._exit_state)

    @property
    def background_class(self) -> str:
        """Returns the background class to use for the particular exit state."""
        return BACKGROUND_CLASS.get(self._exit_state)

    @property
    def color_class(self) -> str:
        """Returns the color class to use for the particular exit state."""
        return COLOR_CLASS.get(self._exit_state)

    def clear(self) -> None:
        """Clear the events in the event list."""
        self._events = []
        self._title = ""
        self._message = []
        self._exit_state = None

    @property
    def events(self) -> List[Tuple[str, str]]:
        """Returns the list of events."""
        return self._events

    def add_event(self, widget_name: str, event_name: str) -> None:
        """Add an event to the list of events."""
        self._events.append(tuple([widget_name, event_name]))

    @property
    def exit_state(self) -> ExitState:
        """Returns the exit state for this event list."""
        return self._exit_state

    def set_exit_state(self, exit_state: ExitState, message: List[str] = None) -> None:
        """Sets the exit state of the event list and a message if there was a warning or error."""
        self._exit_state = exit_state
        self._message = message if message is not None else []

    def compile_instructions(self) -> str:
        """Compile a set of instructions to reproduce certain behaviour."""
        instructions = ""
        for i, event in enumerate(self._events, start=1):
            instructions += f"{i}. {event[1]} the '{event[0]}' widget\n"
        return instructions
