from importlib.machinery import SourceFileLoader


def run():
    """
    Calls the shared run() function with environment-specific parameters.

    """

    SourceFileLoader("pretf_env", "../pretf_env.py").load_module().run(
        envname="dev", envtype="nonprod", dogs=["bodger", "peanut"]
    )
