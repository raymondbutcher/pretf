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

    # Create a symlink to the modules directory
    # to make module source paths simpler.
    modules_dir = path.top / "modules"
    modules_link = path.root / "modules"
    if modules_link.exists():
        modules_link.unlink()
    modules_link.symlink_to(modules_dir)

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform.
    return workflow.default()
