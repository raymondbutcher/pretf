from pretf import log, workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    workflow.require_files("*.*.auto.tfvars")

    # Flatten the directory structure by creating symlinks from the modules
    # directory and files in the 2 parent directories into the current
    # directory. Note that the paths passed in will be relative to the
    # stack-environment directories and not the directory containing
    # this pretf.workflow.py file.
    created = workflow.mirror_files("../../../modules", "../../*.*", "../*.*")

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform.
    result = workflow.default()

    # Clean up symlinks before returning the result.
    workflow.clean_files(created)

    return result
