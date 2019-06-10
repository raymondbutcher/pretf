from pretf.api import tf
from pretf.aws import get_session, terraform_s3_backend


def terraform(var):

    session = get_session(profile_name=var.aws_profile)

    backend_name = f"pretf-tfstate-{var.envtype}"

    yield terraform_s3_backend(
        bucket=backend_name,
        key="iam-users.tfstate",
        region=var.aws_region,
        session=session,
        table=backend_name,
    )

    yield tf("terraform", {"required_version": "0.12.1"})
