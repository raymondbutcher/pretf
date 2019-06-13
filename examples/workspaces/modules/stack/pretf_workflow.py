from pathlib import Path

from pretf import workflow


def pretf_workflow():

    cwd = Path.cwd()
    stack = cwd.name

    try:
        workspace = (cwd / ".terraform" / "environment").read_text()
    except FileNotFoundError:
        workspace = "default"

    workflow.mirror_files(
        "../modules/stack/stack.tf.py", f"../params/{stack}.{workspace}.auto.tfvars"
    )

    return workflow.default()
