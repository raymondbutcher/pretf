from pretf.api import tf
from pretf.aws import provider_aws, terraform_backend_s3


def terraform(var):
    # Create variables needed by this file.
    yield tf("variable.aws_account_id")
    yield tf("variable.aws_profile")
    yield tf("variable.aws_region", {"type": "string"})
    yield tf("variable.stack", {"type": "string"})
    yield tf("variable.terraform_required_version", {"type": "string"})

    # Create an AWS provider using the account ID and profile
    # from the workspace tfvars file.

    yield provider_aws(
        profile=var.aws_profile, allowed_account_ids=[var.aws_account_id]
    )

    # Create a backend configuration using hardcoded details,
    # because all stacks and workspaces use the same backend.

    backend_aws_profile = "rbutcher"
    backend_aws_region = "eu-west-1"

    backend_name = f"pretf-tfstate-example-workspaces"

    yield terraform_backend_s3(
        bucket=backend_name,
        dynamodb_table=backend_name,
        key=f"{var.stack}.tfstate",
        profile=backend_aws_profile,
        region=backend_aws_region,
        workspace_key_prefix="",
    )

    # Also set the required Terraform version.

    yield tf("terraform", {"required_version": var.terraform_required_version})
