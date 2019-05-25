from pretf import tf


def main(aws_region, **kwargs):
    yield tf('provider.aws', {
        'region': aws_region,
    })
