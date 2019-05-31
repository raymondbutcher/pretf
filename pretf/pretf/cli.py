import sys

from .core import execute, tf
from .version import __version__


def main():
    """
    This is the pretf CLI tool entrypoint.

    """

    # Version command.
    args = sys.argv[1:]
    cmd = args[0] if args else None
    if cmd in ("version", "-v", "-version", "--version"):
        print(f"Pretf v{__version__}")
        execute("terraform", verbose=False)
        return

    # Read configuration.
    config = {}
    try:
        with open("pretf.py") as open_file:
            exec(open_file.read(), config)
    except FileNotFoundError:
        pass

    # Call the custom or default run function.
    if "run" in config:
        exit_code = config["run"]()
    else:
        exit_code = run()

    sys.exit(exit_code)


def run():
    """
    This is the default run function to use if one hasn't been
    defined in a pretf.py file in the current directory.

    The default behaviour is to create *.tf.json files
    from any *.tf.py files in the current directory,
    and then execute Terraform.

    """

    tf.create()
    return execute("terraform")
