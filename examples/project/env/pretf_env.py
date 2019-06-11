from pretf.api import create, execute, mirror, remove


def run():

    # Remove any *.tf.json and *.tfvars.json files from the current directory.
    # This removes leftovers from previous runs; when a *.tf.py file gets
    # deleted, the *.tf.json it created should also be deleted.
    remove()

    # Create symlinks in the current directory to everthing in ../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src/*")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # using a combination of default and environment-specific parameters.
    create()

    # Run Terraform.
    return execute()
