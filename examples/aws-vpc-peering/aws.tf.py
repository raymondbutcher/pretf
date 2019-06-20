from pretf.aws import provider_aws


def pretf_blocks(var):
    """
    Creates an AWS provider block for each AWS profile.

    Unlike standard Terraform, if the profile requires an MFA token
    then you will be prompted and the temporary credentials will be
    injected into the provider block for Terraform to use.

    """

    for alias, profile in var.aws_profiles.items():
        yield provider_aws(
            alias=alias, profile=profile, region=var.aws_region, version=var.aws_version
        )
