from pretf.core import imports


def run():
    """
    Calls the shared run() function with environment-specific parameters.

    """

    with imports("../src"):

        import pretf_env

        pretf_env.run(envname="dev", envtype="nonprod", dogs=["bodger", "peanut"])
