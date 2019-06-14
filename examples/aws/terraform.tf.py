from pretf.api import block
from pretf.aws import terraform_backend_s3


def pretf_blocks(var):

    yield terraform_backend_s3(
        bucket=f"pretf-tfstate-example-aws-{var.aws_account_id}",
        dynamodb_table="pretf-tfstate-example-aws",
        key="terraform.tfstate",
        profile=var.aws_profile,
        region=var.aws_region,
    )

    yield block("terraform", {"required_version": "0.12.1"})
