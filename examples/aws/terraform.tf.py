from pretf.aws import terraform_backend_s3


def pretf_blocks(var):
    yield terraform_backend_s3(
        bucket="pretf-examples-aws",
        dynamodb_table="pretf-examples-aws",
        key="terraform.tfstate",
        region=var.aws_region,
        **var.aws_credentials["nonprod"],
    )
