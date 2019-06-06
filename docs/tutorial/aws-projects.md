## Installation

AWS utilities are provided in a separate package, to keep dependencies of the core Pretf package minimal.

To install the Pretf AWS utilities:

```shell
pip install pretf.aws
```

Additionally, these utilities will make use of [boto-source-profile-mfa](https://github.com/claranet/boto-source-profile-mfa) if it has been installed:

```shell
pip install boto-source-profile-mfa
```

## Terraform S3 backend

Pretf can dynamically generate the [S3 backend](https://www.terraform.io/docs/backends/types/s3.html) configuration, and even create the resources required for the backend.


```python
# terraform.tf.py

from pretf.api import tf
from pretf.aws import get_session, terraform_s3_backend


def terraform(var):

    # This gets a Boto3 session using an AWS profile for credentials,
    # but any Boto3 credentials method will work. If the profile
    # requires an MFA token, you will be prompted. This is something
    # that Terraform by itself does not do.
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
    session = get_session(profile_name=var.aws_profile)

    # This will check for the existence of the specified S3 bucket
    # and DynamoDB table. If they do not exist, you will be prompted
    # to create them with a CloudFormation stack. The AWS credentials
    # will then be exported as environment variables, and a Terraform
    # configuration block for the S3 backend is returned. It is then
    # yielded to be included in the generated JSON file.
    yield terraform_s3_backend(
        bucket=f"pretf-tfstate-{var.envtype}",
        key="custom-dev.tfstate",
        region=var.aws_region,
        session=session,
        table=f"pretf-tfstate-{var.envtype}",
    )

    # It is also a good idea to pin the Terraform version in this file.
    yield tf("terraform", {
        "required_version": "0.12.0",
    })
```

## Multiple AWS accounts

It is easy to work with multiple AWS accounts from the same Terraform stack. This is something that is not possible with Terraform wrappers that rely on environment variables alone, because environment variables can only be used for 1 set of credentials at a time.

```python
# aws.tf.py

from pretf.api import tf
from pretf.aws import get_frozen_credentials


def terraform(var):

    nonprod_creds = get_frozen_credentials(profile_name=var.aws_profile_nonprod)

    yield = tf("provider.aws", {
        "alias": "nonprod",
        "region": var.aws_region,
        "access_key": nonprod_creds.access_key,
        "secret_key": nonprod_creds.secret_key,
        "token": nonprod_creds.token,
    })

    prod_creds = get_frozen_credentials(profile_name=var.aws_profile_prod)

    yield = tf("provider.aws", {
        "alias": "prod",
        "region": var.aws_region,
        "access_key": prod_creds.access_key,
        "secret_key": prod_creds.secret_key,
        "token": prod_creds.token,
    })
```
