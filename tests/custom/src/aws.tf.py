from pretf import tf


def main(aws_region, **kwargs):
    """
    This function would normally be a generator,
    but it can also be a regular function that returns a list.

    """

    return [tf("provider.aws", {"region": aws_region})]
