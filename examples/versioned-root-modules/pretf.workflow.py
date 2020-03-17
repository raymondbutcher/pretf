import re

from pretf import workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    found = workflow.require_files("*.auto.tfvars")

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform.
    return workflow.default()
