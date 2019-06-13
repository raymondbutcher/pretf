import sys
from pathlib import Path

from pretf import workflow
from pretf.api import log


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


def run():
    if requires_backend():
        use_workspace_tfvars()
        return workflow.default()
    else:
        return workflow.execute_terraform(verbose=False)


def use_workspace_tfvars():

    cwd = Path.cwd()

    # Delete the existing workspace tfvars file.
    auto_tfvars = cwd / "workspace.auto.tfvars"
    try:
        auto_tfvars.unlink()
    except FileNotFoundError:
        pass

    # Get the current workspace.
    try:
        workspace = (cwd / ".terraform" / "environment").read_text()
    except FileNotFoundError:
        workspace = "default"

    # If there is a tfvars file for this workspace, a *.auto.tfvars
    # symlink so that Pretf and Terraform use it automatically.
    workspace_tfvars = cwd / "workspaces" / f"{workspace}.tfvars"
    if workspace_tfvars.exists():
        auto_tfvars = cwd / "workspace.auto.tfvars"
        auto_tfvars.symlink_to(workspace_tfvars)

    log.ok(f"workspace: {workspace}")
