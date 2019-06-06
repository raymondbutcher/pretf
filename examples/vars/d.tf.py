from pretf.api import tf


def terraform(var):
    yield tf("output.five", {"value": var.five})

    yield tf("output.six", {"value": var.six})

    yield tf("output.seven", {"value": var.seven})
