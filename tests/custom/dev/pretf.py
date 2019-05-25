from pretf import create, execute, remove


def run():

    params = {
        "aws_profile": "rbutcher",
        "aws_region": "eu-west-1",
        "envname": "dev",
        "envtype": "nonprod",
    }

    created = create("../src", **params)

    remove("*.tf.json", exclude=created)

    execute("terraform", default_args=["validate"])
