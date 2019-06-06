from pretf.api import tf


def terraform(var):
    yield tf("variable.one", {"default": 1})

    yield tf("output.one", {"value": var.one})

    yield tf("variable.two", {"default": 2})
