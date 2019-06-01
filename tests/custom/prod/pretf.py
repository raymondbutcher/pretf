from importlib.machinery import SourceFileLoader


def run():
    """
    Calls the shared run() function with environment-specific parameters.

    """

    SourceFileLoader("pretf_env", "../src/pretf_env.py").load_module().run(
        envname="prod", envtype="prod", dogs=["cornelius", "cotton", "bandit"]
    )
