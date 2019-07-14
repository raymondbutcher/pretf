# Pretf examples

This directory contains various examples of how to use Pretf.

## AWS credentials

The credentials in these examples are unsual because:

* Different examples have different mixtures of:
    * Credentials for backend in nonprod, prod, or both AWS accounts.
    * Credentials for resources in nonprod, prod, or both AWS accounts.
* All examples are tested with a single `pytest` command.
* Credentials are automated when running locally.
* It also runs in an Azure DevOps pipeline.

To allow all of the above to work, these examples use an `aws_credentials` variable that contains credentials for both nonprod and prod AWS accounts. Each stack/environment uses the credentials for the relevant account, ignoring the other account if it isn't used.

The default value for `aws_credentials` contains AWS profiles for local usage. The CI environment overrides this value with its own credentials using access keys instead of profiles.

### Running locally

Add these profiles to your AWS credentials configuration:

* `pretf-nonprod`
* `pretf-prod`

### Running in CI environments

Set this environment variable:

```sh
TF_VAR_aws_credentials='{ nonprod = { access_key = "REDACTED", secret_key="REDACTED" }, prod = { access_key = "REDACTED", secret_key="REDACTED" } }
```

Or pass it in as a Terraform CLI argument:

```sh
terraform plan \
  -var 'aws_credentials={ nonprod = { access_key = "REDACTED", secret_key="REDACTED" }, prod = { access_key = "REDACTED", secret_key="REDACTED" } }'
```
