from pretf.api import tf
from pretf.aws import terraform_backend_s3


def terraform(var):

    backend_name = f"pretf-tfstate-{var.envtype}"

    yield terraform_backend_s3(
        bucket=backend_name,
        dynamodb_table=backend_name,
        key="security-groups.tfstate",
        profile=var.aws_profile,
        region=var.aws_region,
    )

    yield tf("terraform", {"required_version": "0.12.1"})
