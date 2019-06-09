import os
import sys

from . import log
from .api import create, execute, remove
from .util import import_file
from .variables import VariableError
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
        execute(verbose=False)
        return

    try:

        # Call the custom or default run function.
        if os.path.exists("pretf.py"):
            with import_file("pretf.py") as pretf:
                exit_code = pretf.run()
        else:
            exit_code = run()

    except VariableError as error:
        if hasattr(error, "errors"):
            for error in error.errors:
                log.bad(str(error))
        else:
            log.bad(str(error))
        exit_code = 1

    sys.exit(exit_code)


def run():
    """
    This is the default run function to use if one hasn't been
    defined in a pretf.py file in the current directory.

    """

    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    create()

    # Execute Terraform.
    return execute()
