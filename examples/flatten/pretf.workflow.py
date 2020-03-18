from pretf import workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    workflow.require_files("*.*.auto.tfvars")

    # Flatten the directory structure by creating symlinks from the modules
    # directory and files in the 2 parent directories into the current
    # directory. Note that the paths passed in will be relative to the
    # stack-environment directories and not the directory containing
    # this pretf.workflow.py file.
    created = workflow.mirror_files("*.tf", "*.tf.py", "modules")

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform. Pass in the mirrored files
    # so they can be cleaned up.
    return workflow.default(created=created)
