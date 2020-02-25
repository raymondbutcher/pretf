import re

from pretf import workflow


def pretf_workflow(path):
    # Restrict where pretf/terraform can run to directories containing an auto
    # tfvars file. It will show an error when running in the wrong directory.
    found = workflow.require_files("*.auto.tfvars")

    # Parse the tfvars file to find the root module source.
    tfvars = found["*.auto.tfvars"][0].read_text()
    match = re.search('# pretf: root_module_source = "(.+?)"', tfvars)
    root_module_source = match.group(1)

    # Fetch the root module into a hidden cache directory and create symlinks
    # to the module contents in the current working directory.
    created = workflow.mirror_files(
        from_module=root_module_source,
        verbose=True,
    )

    # Now run the standard Pretf workflow which generates files
    # and then executes Terraform. Pass in the mirrored files
    # so they can be cleaned up.
    return workflow.default(created=created)
