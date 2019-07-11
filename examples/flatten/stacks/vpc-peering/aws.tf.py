from pretf.aws import provider_aws


def pretf_blocks(var):
    yield provider_aws(
        alias="dev",
        region=var.aws_region,
        **var.aws_credentials_dev,
    )
    yield provider_aws(
        alias="prod",
        region=var.aws_region,
        **var.aws_credentials_prod,
    )
