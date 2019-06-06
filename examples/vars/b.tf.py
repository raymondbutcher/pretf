from pretf.api import tf


def terraform(var):
    yield tf("output.two_attr", {"value": var.two})

    yield tf("output.two_dict", {"value": var["two"]})

    yield tf("variable.three", {"default": 3})

    yield tf("output.three", {"value": var.three})

    yield tf("variable.four")

    yield tf("output.four", {"value": var.four})
