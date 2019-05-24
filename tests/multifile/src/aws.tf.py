from pretf import tf


def main(params):
    yield tf('provider.aws', {
        'region': params.aws_region,
    })
