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

## AWS providers

Pretf can generate AWS provider blocks, with full support for MFA prompts.

```python
# aws.tf.py

from pretf.aws import provider_aws


def pretf_blocks(var):
    yield provider_aws(
        profile=var.aws_profile,
        region=var.aws_region,
    )
```

## Terraform S3 backend

Pretf can dynamically generate the [S3 backend](https://www.terraform.io/docs/backends/types/s3.html) configuration, and even create the resources required for the backend.

```python
# terraform.tf.py

from pretf.aws import terraform_backend_s3


def pretf_blocks(var):
    # This will check for the existence of the specified S3 bucket
    # and DynamoDB table. If they do not exist, you will be prompted
    # to create them with a CloudFormation stack. The AWS credentials
    # will then be exported as environment variables, and a Terraform
    # configuration block for the S3 backend is returned. It is then
    # yielded to be included in the generated JSON file.
    yield terraform_backend_s3(
        bucket=f"pretf-tfstate-{var.envtype}",
        dynamodb_table=f"pretf-tfstate-{var.envtype}",
        key="terraform.tfstate",
        profile=var.aws_profile,
        region=var.aws_region,
    )
```

## Terraform S3 remote state

Pretf can generate S3 remote state data source blocks, with full support for MFA prompts.

```python
# terraform.tf.py

from pretf.aws import terraform_remote_state_s3


def pretf_blocks(var):
    yield terraform_remote_state_s3("ecs_cluster", config={
        "bucket": var.ecs_cluster_remote_state["bucket"],
        "key": var.ecs_cluster_remote_state["key"],
        "profile": var.ecs_cluster_remote_state["profile"],
        "region": var.ecs_cluster_remote_state["region"],
    })
```

## Multiple AWS accounts

It is easy to work with multiple AWS accounts from the same Terraform stack. This is something that is not possible with Terraform wrappers that rely on environment variables alone, because environment variables can only be used for 1 set of credentials at a time.

```python
# aws.tf.py

from pretf.aws import provider_aws


def pretf_blocks(var):
    for alias, profile in var.aws_profiles.items():
        yield provider_aws(
            alias=alias,
            profile=profile,
            region=var.aws_region,
        )
```
