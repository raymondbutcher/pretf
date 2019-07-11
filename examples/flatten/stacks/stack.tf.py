from pretf.api import block
from pretf.aws import provider_aws, terraform_backend_s3


def pretf_blocks(var):

    # Create variables needed by this file.

    yield block("variable", "aws_profile", {"type": "string"})
    yield block("variable", "aws_region", {"type": "string"})
    yield block("variable", "environment", {"type": "string"})
    yield block("variable", "stack", {"type": "string"})
    yield block("variable", "terraform_required_version", {"type": "string"})

    # Create a backend configuration using the environment details.
    # Stacks in the same account share backend resources.

    if var.environment == 'prod':
        backend = "pretf-tfstate-prod"
    else:
        backend = "pretf-tfstate-nonprod"

    yield terraform_backend_s3(
        bucket=backend,
        dynamodb_table=backend,
        key=f"flatten/{var.stack}/terraform.tfstate",
        profile=var.aws_profile,
        region=var.aws_region,
    )

    # Create a default AWS provider for this environment.

    yield provider_aws(
        profile=var.aws_profile,
        region=var.aws_region,
    )

    # Also set the required Terraform version.

    yield block("terraform", {"required_version": var.terraform_required_version})
