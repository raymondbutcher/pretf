from os.path import relpath
from pathlib import Path

from pretf import workflow
from pretf.api import log

TOP_PATH = Path(__file__).parent
PARAMS_PATH = TOP_PATH / "params"
STACKS_PATH = TOP_PATH / "stacks"


def pretf_workflow(path, terraform):
    # Restrict where pretf/terraform can run to the stack directories.
    if path.cwd.parent != STACKS_PATH:
        log.bad("you are not in a stack directory")
        stack_dirs = [p for p in sorted(STACKS_PATH.iterdir()) if p.is_dir()]
        if stack_dirs:
            log.bad("found:")
            for stack_dir in stack_dirs:
                log.bad(f"* {relpath(stack_dir)}")
        return 1

    stack = path.cwd.name
    workspace = terraform.workspace

    # Symlink stack.tf.py into the current directory,
    # which handles the AWS provider and S3 backend.
    # Also get the tfvars file for the current workspace.
    workflow.delete_links()
    created = workflow.link_files(
        STACKS_PATH / "stack.tf.py",
        PARAMS_PATH / f"{stack}.{workspace}.auto.tfvars",
    )

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform.
    return workflow.default(created=created)
