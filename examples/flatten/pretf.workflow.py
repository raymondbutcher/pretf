from pretf import workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    workflow.require_files("*.*.auto.tfvars")

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform. Pass in the mirrored files
    # so they can be cleaned up.
    return workflow.default()
