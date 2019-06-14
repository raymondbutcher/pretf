from pretf import workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    workflow.require_files("*.*.auto.tfvars")

    # Flatten the directory structure by creating symlinks from the 2 parent
    # directories into the current directory. Note that the current directory
    # will be one of the stack-environment directories and not the directory
    # containing this pretf.py workflow file.
    workflow.mirror_files("../../*", "../*", include_directories=False)

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform.
    return workflow.default()
