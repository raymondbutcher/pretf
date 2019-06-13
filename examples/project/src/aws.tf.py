from pretf.aws import provider_aws


def pretf_blocks(var):
    """
    This shows how to use pretf_aws for multiple AWS providers.
    This allows for a single Terraform stack to manage resources
    in multiple accounts. However, in this test I am using the
    same account twice.

    """

    yield provider_aws(profile=var.aws_profile, region=var.aws_region)

    yield provider_aws(profile=var.aws_profile, region="eu-west-1", alias="london")
