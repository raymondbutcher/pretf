from pretf.api import block
from pretf.aws import provider_aws, terraform_backend_s3


def pretf_blocks(var):

    # Create variables needed by this file.

    yield block("variable", "aws_credentials", {
        "default": {
            "nonprod": {
                "profile": "pretf-nonprod",
            },
            "prod": {
                "profile": "pretf-prod",
            },
        },
    })
    yield block("variable", "aws_region", {
        "default": "eu-west-1",
    })
    yield block("variable", "environment", {
        "type": "string",
    })
    yield block("variable", "stack", {
        "type": "string",
    })

    # Create a backend configuration using the environment details.
    # Stacks in the same account share backend resources.

    if var.environment == 'prod':
        account = "prod"
    else:
        account = "nonprod"

    backend = f"pretf-examples-enterprise-{account}"

    yield terraform_backend_s3(
        bucket=backend,
        dynamodb_table=backend,
        key=f"{var.stack}/terraform.tfstate",
        region=var.aws_region,
        **var.aws_credentials[account],
    )

    # Create a default AWS provider for this environment.

    yield provider_aws(
        region=var.aws_region,
        **var.aws_credentials[account],
    )
