def pretf_files():
    # This creates symlinks from the specified paths
    # into the working directory.

    # Automatically figures out the paths to use by checking
    # the working directory and then each parent directory up to
    # the pretf.workflow.py file until it finds a match.

    yield "stack.auto.tfvars"
    yield "stack.tf.py"
