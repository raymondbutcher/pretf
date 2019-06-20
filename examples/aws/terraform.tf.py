from pretf.aws import terraform_backend_s3


def pretf_blocks(var):
    yield terraform_backend_s3(
        bucket="pretf-tfstate-nonprod",
        dynamodb_table="pretf-tfstate-nonprod",
        key="examples/aws/terraform.tfstate",
        profile=var.aws_profile,
        region=var.aws_region,
    )
