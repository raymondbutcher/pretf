from pretf.api import block
from pretf.aws import provider_aws, terraform_backend_s3


def pretf_blocks(terraform, var):

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

    # Create a backend configuration in the prod account,
    # because all workspaces must use the same backend.

    yield terraform_backend_s3(
        bucket="pretf-examples-workspaces",
        dynamodb_table="pretf-examples-workspaces",
        key=f"{var.stack}/terraform.tfstate",
        region="eu-west-1",
        workspace_key_prefix="",
        **var.aws_credentials["prod"],
    )

    # Create a default AWS provider for this workspace.

    if terraform.workspace == "prod":
        account = "prod"
    else:
        account = "nonprod"

    yield provider_aws(
        region=var.aws_region,
        **var.aws_credentials[account],
    )
