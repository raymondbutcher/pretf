from pretf.core import import_file


def run():
    """
    Calls the shared run() function with environment-specific parameters.

    """

    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run_with_params(
            envname="prod", envtype="prod", dogs=["cornelius", "cotton", "bandit"]
        )
