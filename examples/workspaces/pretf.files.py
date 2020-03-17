def pretf_files(path, terraform):
    # Symlink stack.tf.py into the current directory,
    # which handles the AWS provider and S3 backend.
    yield "stack.tf.py"

    # Also get the tfvars file for the current workspace.
    stack = path.cwd.name
    workspace = terraform.workspace
    yield f"params/{stack}.{workspace}.auto.tfvars"
