import sys
from pathlib import Path

from pretf.api import create, execute, log, mirror, remove


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
    # For some simple commands, just run Terraform.
    if not requires_backend():
        return execute(verbose=False)

    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Mirror the workspace file into the working directory.
    # This creates configuration for the AWS provider and S3 backend.
    mirror("../src/workspace.tf.py")

    # Create a symlink from "workspaces/{workspace}/terraform.tfvars"
    # to "workspace.auto.tfvars" to automatically use those variables.
    use_workspace_tfvars()

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    create()

    # Execute Terraform.
    return execute()


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
