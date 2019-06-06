## export_environment_variables

Sets environment variables for AWS credentials using the provided [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) or [boto3.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) arguments. This should usually not be necessary because `terraform_s3_backend()` does this automatically.

Signature:

```python
export_environment_variables(session=None, **kwargs)

session:
    optional boto3.Session
**kwargs:
    optional arguments for creating a boto3.Session

returns:
    None
```

Example:

```python
from pretf.aws import export_environment_variables


def run():
    export_environment_variables(profile_name="example")

def terraform(var):
    export_environment_variables(profile_name=var.aws_profile)
```

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


def run():
    account_id = get_account_id(profile_name="example")


def terraform(var):
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


def run():
    creds = get_frozen_credentials(profile_name="example")


def terraform(var):
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


def run():
    session = get_session(profile_name="example")


def terraform(var):
    session = get_session(profile_name=var.aws_profile)
```

## terraform_s3_backend

Ensures that the S3 backend exists, prompting to create it if necessary, sets the credentials as environment variables, then returns a Terraform configuration block for it.

Signature:

```python
terraform_s3_backend(session, bucket, key, table, region=None)

session:
    required boto3.Session
bucket:
    required str for the S3 bucket name to use for storing the Terraform state file
key:
    required str for the S3 object key to use for storing the Terraform state file
table:
    required str for the DynamoDB table to use for locking the Terraform state file
region:
    option str for the AWS region, defaults to the session region

returns:
    Block
```

Example:

```python
from pretf.aws import terraform_s3_backend


def terraform(var):
    session = get_session(profile_name=var.aws_profile)
    yield terraform_s3_backend(
        bucket="example-tfstate-bucket",
        key="terraform.tfstate",
        region="eu-west-1",
        session=session,
        table="example-tfstate-table",
    )
```
