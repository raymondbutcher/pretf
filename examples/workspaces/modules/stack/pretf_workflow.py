import sys
from pathlib import Path

from pretf import workflow
from pretf.api import log


def pretf_workflow():
    if requires_backend():
        cwd = Path.cwd()
        stack = cwd.name
        try:
            workspace = (cwd / ".terraform" / "environment").read_text()
        except FileNotFoundError:
            workspace = "default"
        workflow.mirror_files(
            "../modules/stack/stack.tf.py",
            f"../params/{stack}.{workspace}.auto.tfvars",
        )
        return workflow.default()
    else:
        return workflow.execute_terraform(verbose=False)


def requires_backend():
    workspace_command = False
    for arg in sys.argv[1:]:
        if arg == "fmt":
            return False
        elif arg == "workspace":
            workspace_command = True
        elif not arg.startswith("-"):
            if workspace_command:
                if arg == "show":
                    return False
                else:
                    return True
            else:
                return True
    return False

