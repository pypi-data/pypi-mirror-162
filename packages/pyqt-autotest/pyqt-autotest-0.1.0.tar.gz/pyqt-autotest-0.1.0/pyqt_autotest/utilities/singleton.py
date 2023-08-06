# Project Repository : https://github.com/robertapplin/pyqt-autotest
# Authored by Robert Applin, 2022

class Singleton(type):
    """A class used for creating a singleton class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
