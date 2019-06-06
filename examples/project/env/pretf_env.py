from pretf.run import create, execute, mirror, remove


def run_with_params(**params):

    default_params = {"aws_profile": "rbutcher", "aws_region": "eu-west-1"}
    combined_params = dict(default_params, **params)

    # Remove any *.tf.json files from the current directory.
    # This removes leftovers from previous runs; when a *.tf.py file gets
    # deleted, the *.tf.json it created should also be deleted.
    remove()

    # Create symlinks in the current directory to everthing in ../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # using a combination of default and environment-specific parameters.
    create(**combined_params)

    # Run Terraform, defaulting to the validate command.
    return execute()
