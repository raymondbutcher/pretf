from pretf.api import tf
from pretf.aws import get_frozen_credentials


def terraform(var):
    """
    This shows how to use pretf_aws to get AWS credentials
    and use them in multiple providers. This allows for a single
    Terraform stack to manage resources in multiple accounts.
    However, in this test I am using the same account twice.

    This also demonstrates returning a standard dictionary
    instead of using the tf object.

    """

    # Normally you would not need to use creds here,
    # and rely on environment variables set by terraform.tf.py
    # but this shows how to work with multiple AWS accounts.

    creds = get_frozen_credentials(profile_name=var.aws_profile)

    yield tf(
        "provider.aws",
        {
            "region": var.aws_region,
            "access_key": creds.access_key,
            "secret_key": creds.secret_key,
            "token": creds.token,
        },
    )

    yield {
        "provider": {
            "aws": {
                "alias": "london",
                "region": "eu-west-2",
                "access_key": creds.access_key,
                "secret_key": creds.secret_key,
                "token": creds.token,
            }
        }
    }
