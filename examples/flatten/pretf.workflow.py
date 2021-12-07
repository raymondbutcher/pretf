from pretf import workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    workflow.require_files("*.*.auto.tfvars")

    # Flatten the directory structure into the working directory.
    # First delete any leftover files from previous failed runs.
    workflow.delete_files("tmp-*")
    created = workflow.copy_files("*.tf", "*.tf.py", "*.tfvars.py", prefix="tmp-")

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform. Pass in the copied files
    # so they can be cleaned up.
    return workflow.default(created=created)
