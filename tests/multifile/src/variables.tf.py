from pretf import tf


def main(params):
    yield tf('variable.aws_region', {
        'default': params.aws_region,
    })
