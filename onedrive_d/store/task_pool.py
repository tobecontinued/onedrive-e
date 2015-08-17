__author__ = 'xb'


class NoTaskException(Exception):
    pass


class TaskPool:
    """
    An in-memory storage for Tasks based on hash maps.
    """

    def __init__(self):
        self.tasks_by_path = {}

    def add_task(self, task):
        pass

    def pop_task(self):
        pass
