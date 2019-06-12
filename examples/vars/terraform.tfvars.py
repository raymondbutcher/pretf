from pretf.api import block


def terraform(var):
    yield block("three", 3)

    yield block("four", 4)
