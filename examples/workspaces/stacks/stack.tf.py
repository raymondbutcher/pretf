from pretf.api import block
from pretf.aws import provider_aws, terraform_backend_s3


def pretf_blocks(var):

    # Create variables needed by this file.

    yield block("variable", "aws_profile", {"type": "string"})
    yield block("variable", "aws_region", {"type": "string"})
    yield block("variable", "stack", {"type": "string"})
    yield block("variable", "terraform_required_version", {"type": "string"})

    # Create a backend configuration using hardcoded details,
    # because all stacks and workspaces use the same backend.

    backend_aws_profile = "pretf"
    backend_aws_region = "eu-west-1"

    backend_name = "pretf-tfstate-example-workspaces"

    yield terraform_backend_s3(
        bucket=backend_name,
        dynamodb_table=backend_name,
        key=f"{var.stack}.tfstate",
        profile=backend_aws_profile,
        region=backend_aws_region,
        workspace_key_prefix="",
    )

    # Create a default AWS provider for this environment.

    yield provider_aws(
        profile=var.aws_profile,
        region=var.aws_region,
    )

    # Also set the required Terraform version.

    yield block("terraform", {"required_version": var.terraform_required_version})
