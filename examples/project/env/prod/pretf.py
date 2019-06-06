from pretf.util import import_file


def run():
    """
    Calls the shared run() function.

    """

    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run()
