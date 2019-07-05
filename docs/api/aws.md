## get_account_id

Returns the AWS account ID for the provided [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) or [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) arguments.

Signature:

```python
get_account_id(session=None, **kwargs)

session:
    optional boto3.Session
**kwargs:
    optional arguments for creating a boto3.Session

returns:
    str
```

Example:

```python
from pretf.aws import get_account_id


def pretf_workflow():
    account_id = get_account_id(profile_name="example")


def pretf_blocks(var):
    account_id = get_account_id(profile_name=var.aws_profile)
```

## get_frozen_credentials

Returns AWS credentials for the provided [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) or [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) arguments.

Signature:

```python
get_frozen_credentials(session=None, **kwargs)

session:
    optional boto3.Session
**kwargs:
    optional arguments for creating a boto3.Session

returns:
    botocore.credentials.ReadOnlyCredentials
```

Example:

```python
from pretf.aws import get_frozen_credentials


def pretf_workflow():
    creds = get_frozen_credentials(profile_name="example")


def pretf_blocks(var):
    creds = get_frozen_credentials(profile_name=var.aws_profile)
```

## get_session

Returns a [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html). Uses [boto-source-profile-mfa](https://github.com/claranet/boto-source-profile-mfa) if installed.

Signature:

```python
get_session(**kwargs)

**kwargs:
    optional arguments for creating a boto3.Session

returns:
    botocore.credentials.ReadOnlyCredentials
```

Example:

```python
from pretf.aws import get_session


def pretf_workflow():
    session = get_session(profile_name="example")


def pretf_blocks(var):
    session = get_session(profile_name=var.aws_profile)
```

## provider_aws

Returns an [AWS provider](https://www.terraform.io/docs/providers/aws/index.html) block. In cases where Terraform might not support the `profile` option, it will be replaced with static credentials so that Terraform can use them instead. This is particularly useful when the `profile` needs to prompt for an MFA token, which Terraform does not support.

Signature:

```python
provider_aws(**body)

**body:
    required dict of configuration options as per Terraform documentation

returns:
    Block
```

Example:

```python
from pretf.aws import provider_aws


def pretf_blocks(var):
    yield provider_aws(
        profile=var.aws_profile,
        region=var.aws_region,
    )
```

## terraform_backend_s3

Ensures that the S3 backend exists, prompting to create it if necessary, sets the credentials as environment variables in some cases, and returns a Terraform configuration block for it. Accepts the same options as the [S3 backend configuration variables](https://www.terraform.io/docs/backends/types/s3.html#configuration-variables).

Signature:

```python
terraform_backend_s3(bucket, dynamodb_table, **config)

bucket:
    required str for the S3 bucket name to use for storing the Terraform state file
dynamodb_table:
    required str for the DynamoDB table to use for locking the Terraform state file
**config:
    required dict of other configuration options as per Terraform documentation

returns:
    Block
```

Example:

```python
from pretf.aws import terraform_backend_s3


def pretf_blocks(var):
    yield terraform_backend_s3(
        bucket="example-tfstate-bucket",
        dynamodb_table="example-tfstate-table",
        key="terraform.tfstate",
        profile=var.aws_profile,
        region="eu-west-1",
    )
```
