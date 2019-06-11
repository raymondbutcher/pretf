from pretf.api import tf
from pretf.aws import provider_aws


def terraform(var):
    """
    This shows how to use pretf_aws for multiple AWS providers.
    This allows for a single Terraform stack to manage resources
    in multiple accounts. However, in this test I am using the
    same account twice.

    """

    yield provider_aws(profile=var.aws_profile, region=var.aws_region)

    london = yield provider_aws(profile=var.aws_profile, region="eu-west-1", alias="london")

    print(london.alias)
