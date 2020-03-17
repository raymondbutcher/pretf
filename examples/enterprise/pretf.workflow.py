import re

from pretf import workflow


def pretf_workflow(path):
    # Restrict where Pretf/Terraform can run to directories containing a
    # tfvars file. It will show an error when running in the wrong directory.
    workflow.require_files("terraform.tfvars")

    # Now run the standard Pretf workflow which generates files,
    # executes Terraform, then cleans up files.
    return workflow.default()
