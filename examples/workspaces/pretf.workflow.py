from os.path import relpath
from pathlib import Path

from pretf import workflow
from pretf.api import log


def pretf_workflow(path, terraform):
    # Restrict where pretf/terraform can run to the stack directories.
    stacks_dir = Path(__file__).parent / "stacks"
    if path.cwd.parent != stacks_dir:
        log.bad("you are not in a stack directory")
        stack_dirs = [p for p in sorted(stacks_dir.iterdir()) if p.is_dir()]
        if stack_dirs:
            log.bad("found:")
            for stack_dir in stack_dirs:
                log.bad(f"* {relpath(stack_dir)}")
        return 1

    # Symlink stack.tf.py into the current directory,
    # which handles the AWS provider and S3 backend.
    # Also get the tfvars file for the current workspace.
    stack = path.cwd.name
    workspace = terraform.workspace
    created = workflow.mirror_files(
        "../stack.tf.py", f"../../params/{stack}.{workspace}.auto.tfvars"
    )

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform.
    return workflow.default(created=created)
