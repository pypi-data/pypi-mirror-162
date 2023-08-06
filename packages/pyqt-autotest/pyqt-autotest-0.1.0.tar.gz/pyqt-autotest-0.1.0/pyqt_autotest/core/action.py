# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022
from enum import Enum


class Action(str, Enum):
    """The actions that are already implemented for auto testing."""
    KeyDownClick = "Press the down key on"
    KeyUpClick = "Press the up key on"
    MouseLeftClick = "Left click"

    def __str__(self) -> str:
        return self.value
