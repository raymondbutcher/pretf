from pretf.aws import provider_aws


def pretf_blocks(var):
    yield provider_aws(
        alias="dev",
        region=var.aws_region,
        **var.aws_credentials["nonprod"],
    )
    yield provider_aws(
        alias="prod",
        region=var.aws_region,
        **var.aws_credentials["prod"],
    )
