from pretf.api import block
from pretf.aws import provider_aws, terraform_backend_s3


def pretf_blocks(var):
    # Create variables needed by this file.
    yield block("variable", "aws_account_id", {})
    yield block("variable", "aws_profile", {})
    yield block("variable", "aws_region", {"type": "string"})
    yield block("variable", "stack", {"type": "string"})
    yield block("variable", "terraform_required_version", {"type": "string"})

    # Create an AWS provider using details from the current directory's tfvars file.

    yield provider_aws(
        profile=var.aws_profile, allowed_account_ids=[var.aws_account_id]
    )

    # Create a backend configuration using the environment details.
    # Stacks in the same account share backend resources.

    yield terraform_backend_s3(
        bucket=f"pretf-tfstate-example-flatten-{var.aws_account_id}",
        dynamodb_table="pretf-tfstate-example-flatten",
        key=f"{var.stack}.tfstate",
        profile=var.aws_profile,
        region=var.aws_region,
    )

    # Also set the required Terraform version.

    yield block("terraform", {"required_version": var.terraform_required_version})
