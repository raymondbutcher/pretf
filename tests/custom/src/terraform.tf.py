from pretf.aws import get_session, s3_backend
from pretf.core import tf


def terraform(aws_profile, aws_region, envtype, **kwargs):

    session = get_session(profile_name=aws_profile)

    backend_name = f"pretf-tfstate-{envtype}"

    yield s3_backend(
        bucket=backend_name,
        key="custom-dev.tfstate",
        region=aws_region,
        session=session,
        table=backend_name,
    )

    yield tf("terraform", {"required_version": "0.12.0"})
