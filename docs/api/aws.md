## export_environment_variables

```python
from pretf.aws import export_environment_variables


def run():
    export_environment_variables(profile_name="example")

def terraform():
    export_environment_variables(profile_name="example")
```

## get_account_id

```python
from pretf.aws import get_account_id


def run():
    account_id = get_account_id(profile_name="example")


def terraform():
    account_id = get_account_id(profile_name="example")
```

## get_frozen_credentials

```python
from pretf.aws import get_frozen_credentials


def run():
    creds = get_frozen_credentials(profile_name="example")


def terraform():
    creds = get_frozen_credentials(profile_name="example")
```

## get_session

```python
from pretf.aws import get_session


def run():
    session = get_session(profile_name="example")


def terraform():
    session = get_session(profile_name="example")
```

## terraform_s3_backend

```python
from pretf.aws import terraform_s3_backend


def terraform():
    session = get_session(profile_name="example")
    yield terraform_s3_backend(
        bucket="example-tfstate-bucket",
        key="terraform.tfstate",
        region="eu-west-1",
        session=session,
        table="example-tfstate-table",
    )
```
