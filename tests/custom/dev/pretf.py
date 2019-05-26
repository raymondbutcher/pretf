from pretf import create, execute, mirror, remove


def run():

    # Define environment-specific parameters to pass into *.tf.py functions.
    # These could easily be read from a file or other data source if preferred.
    params = {
        "aws_profile": "rbutcher",
        "aws_region": "eu-west-1",
        "envname": "dev",
        "envtype": "nonprod",
    }

    # Create symlinks in the current directory to everthing in ../src
    # This deletes any other symlinks in the current directory
    mirror("../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created.
    created = create(**params)

    # Remove any *.tf.json files from the current directory that were not
    # created just now. This removes orphans from previous runs; when a
    # *.tf.py file is deleted, the *.tf.json it created previously
    # should be deleted.
    remove("*.tf.json", exclude=created)

    # Run Terraform, defaulting to the validate command.
    execute("terraform", default_args=["validate"])
