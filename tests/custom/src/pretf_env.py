from pretf.core import execute, mirror, tf


def run(**params):

    default_params = {"aws_profile": "rbutcher", "aws_region": "eu-west-1"}
    combined_params = dict(default_params, **params)

    # Create symlinks in the current directory to everthing in ../src
    # This deletes any other symlinks in the current directory
    mirror("../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # using a combination of default and environment-specific parameters.
    created = tf.create(**combined_params)

    # Remove any *.tf.json files from the current directory that were not
    # created just now. This removes orphans from previous runs; when a
    # *.tf.py file is deleted, the *.tf.json it created previously
    # should be deleted.
    tf.remove(exclude=created)

    # Run Terraform, defaulting to the validate command.
    execute("terraform", default_args=["validate"])
