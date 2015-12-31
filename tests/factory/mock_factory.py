import atexit


def mock_register():
    def register(func, **kwargs):
        pass

    atexit.register = register
