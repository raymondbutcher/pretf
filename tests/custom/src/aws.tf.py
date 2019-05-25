from pretf import tf


def terraform(aws_region, **kwargs):
    """
    This function would normally be a generator,
    but it can also be a regular function that returns a list.

    This function also demonstrates returning a standard dictionary
    instead of using the tf object.

    """

    tf_block = tf("provider.aws", {"region": aws_region})

    dict_block = {"provider": {"aws": {"alias": "london", "region": "eu-west-2"}}}

    return [tf_block, dict_block]
