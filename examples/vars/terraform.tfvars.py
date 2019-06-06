from pretf.api import tf


def terraform(var):
    yield tf("three", 3)

    yield tf("four", 4)
