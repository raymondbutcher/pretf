from pretf.aws import provider_aws


def pretf_blocks(var):
    yield provider_aws(
        region=var.aws_region,
        **var.aws_credentials["nonprod"],
    )
