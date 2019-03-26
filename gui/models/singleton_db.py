class Singleton(object):
    """
    In software engineering, the singleton pattern is a software design pattern that restricts the instantiation of a
    class to one "single" instance. This is useful when exactly one object is needed to coordinate actions across
    the system. https://en.wikipedia.org/wiki/Singleton_pattern


    Alex Martelli implementation of Singleton (Borg)
    http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html

    Also check:
    https://stackoverflow.com/questions/44237186/what-is-the-best-way-to-share-data-between-widgets-with-pyqt?rq=1

    """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Database(Singleton):
    def __init__(self, data_to_store=None):
        Singleton.__init__(self)
        if data_to_store is not None:
            self._data = data_to_store

    def get(self):
        """
        Returns the stored data.

        :return:
        """
        return self._data

    def changeData(self, data):
        """
        Changes (updates) the data stored.
        """
        self._data = data

    def hasData(self):
        """
        Returns a bool indicating if the data attribute is loaded (has data).

        This function enables the database to understand if data has been loaded or not.
        """
        return hasattr(self, "_data")
