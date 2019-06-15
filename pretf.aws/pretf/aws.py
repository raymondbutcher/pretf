import json
import os
from functools import lru_cache
from time import sleep
from typing import Any, Optional

from pretf.api import block, log
from pretf.render import Block

try:
    from boto_source_profile_mfa import get_session as Session  # type: ignore
except ImportError:
    from boto3 import Session  # type: ignore


def _create_s3_backend(
    session: Session, bucket: str, table: str, region_name: str
) -> None:

    # Prompt before creating anything.
    account_id = get_account_id(session)
    bucket_arn = _get_s3_bucket_arn(region_name, account_id, bucket)
    table_arn = _get_dynamodb_table_arn(region_name, account_id, table)
    log.ok(f"backend: {bucket_arn}")
    log.ok(f"backend: {table_arn}")
    if not log.accept(f"backend: create backend resources"):
        log.bad("backend: not created")
        raise SystemExit(1)

    # Use the S3 bucket and DynamoDB table name for the CloudFormation stack.
    if bucket == table:
        stack_name = bucket
    else:
        stack_name = f"{bucket}-{table}"
    stack_arn = _get_cloudformation_stack_arn(region_name, account_id, stack_name)
    log.ok(f"backend: creating {stack_arn}")

    # Create the stack.
    cloudformation_client = session.client("cloudformation", region_name=region_name)
    cloudformation_client.create_stack(
        StackName=stack_name,
        ResourceTypes=["AWS::DynamoDB::Table", "AWS::S3::Bucket"],
        TemplateBody=json.dumps(
            {
                "Resources": {
                    "Table": {
                        "Type": "AWS::DynamoDB::Table",
                        "Properties": {
                            "TableName": table,
                            "AttributeDefinitions": [
                                {"AttributeName": "LockID", "AttributeType": "S"}
                            ],
                            "KeySchema": [
                                {"AttributeName": "LockID", "KeyType": "HASH"}
                            ],
                            "BillingMode": "PAY_PER_REQUEST",
                        },
                    },
                    "Bucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                            "AccessControl": "Private",
                            "BucketName": bucket,
                            "VersioningConfiguration": {"Status": "Enabled"},
                        },
                    },
                }
            }
        ),
    )

    # Wait for it to complete.
    log.ok(f"backend: please wait...")
    while True:
        sleep(10)
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        for stack in response["Stacks"]:
            if stack["StackStatus"] == "CREATE_IN_PROGRESS":
                pass
            elif stack["StackStatus"] == "CREATE_COMPLETE":
                log.ok("backend: create complete")
                return
            else:
                log.bad(f"backend: {stack['StackStatus']}")
                log.bad(f"backend: {stack['StackStatusReason']}")


def _get_cloudformation_stack_arn(
    region_name: str, account_id: str, stack_name: str
) -> str:
    return f"arn:aws:cloudformation:{region_name}:{account_id}:stack/{stack_name}"


def _get_dynamodb_table_arn(region_name: str, account_id: str, table: str) -> str:
    return f"arn:aws:dynamodb:{region_name}:{account_id}:{table}"


def _get_s3_bucket_arn(region_name: str, account_id: str, bucket: str) -> str:
    return f"arn:aws:s3:{region_name}:{account_id}:{bucket}"


def _get_s3_backend_status(
    session: Session, region_name: str, bucket: str, table: str
) -> dict:

    s3_client = session.client("s3")

    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket)
    except s3_client.exceptions.NoSuchBucket:
        bucket_exists = False
        bucket_versioning_enabled = False
    else:
        bucket_exists = True
        bucket_versioning_enabled = response["Status"] == "Enabled"

    dynamodb_client = session.client("dynamodb", region_name=region_name)

    try:
        dynamodb_client.describe_table(TableName=table)
    except dynamodb_client.exceptions.ResourceNotFoundException:
        table_exists = False
    else:
        table_exists = True

    return {
        "bucket_exists": bucket_exists,
        "bucket_versioning_enabled": bucket_versioning_enabled,
        "table_exists": table_exists,
    }


def export_environment_variables(
    session: Optional[Session] = None, region_name: Optional[str] = None, **kwargs: dict
) -> None:
    """
    Exports AWS credentials as environment variables.

    """

    if session is None:
        session = get_session(**kwargs)

    creds = get_frozen_credentials(session)

    if creds.access_key:
        os.environ["AWS_ACCESS_KEY_ID"] = creds.access_key

    if creds.secret_key:
        os.environ["AWS_SECRET_ACCESS_KEY"] = creds.secret_key

    if creds.token:
        os.environ["AWS_SECURITY_TOKEN"] = creds.token
        os.environ["AWS_SESSION_TOKEN"] = creds.token

    if not region_name:
        region_name = session.region_name
    if region_name:
        os.environ["AWS_REGION"] = region_name
        os.environ["AWS_DEFAULT_REGION"] = region_name


@lru_cache()
def get_account_id(session: Optional[Session] = None, **kwargs: dict) -> str:
    if session is None:
        session = get_session(**kwargs)
    sts_client = session.client("sts")
    account_id = sts_client.get_caller_identity()["Account"]
    return account_id


def get_frozen_credentials(session: Optional[Session] = None, **kwargs: dict) -> Any:
    if session is None:
        session = get_session(**kwargs)
    return session.get_credentials().get_frozen_credentials()


@lru_cache()
def get_session(**kwargs: dict) -> Session:
    return Session(**kwargs)


def provider_aws(**body: dict) -> Block:
    """
    Returns an AWS provider block. If provided, the `profile` option
    will be replaced with static credentials.

    """

    if "profile" in body:

        session = get_session(profile_name=body["profile"])

        creds = session.get_credentials()

        if creds.method in ("config-file", "shared-credentials-file"):
            # The credentials were in the config file, so Terraform will
            # have no trouble finding these credentials using the profile.
            # Do nothing to the configuration body.
            pass
        else:
            # The credentials were more complicated, probably using the
            # assume-role provider, custom-process provider, or anything
            # else. In case Terraform is unable to handle these credentials
            # (e.g. it can't do MFA prompts), replace the "profile" in the
            # the configuration body with actual credentials.
            frozen_creds = creds.get_frozen_credentials()
            body["access_key"] = frozen_creds.access_key
            body["secret_key"] = frozen_creds.secret_key
            if creds.token:
                body["token"] = frozen_creds.token
            del body["profile"]

    return block("provider", "aws", body)


def terraform_backend_s3(bucket: str, dynamodb_table: str, **config: Any) -> Block:
    """
    This ensures that the S3 backend exists, prompting to create it
    if necessary, sets the credentials as environment variables,
    then returns a Terraform configuration block for it.

    """

    # Create a session from any AWS credentials options.

    session_kwargs = {}
    session_kwargs_map = {
        "profile": "profile_name",
        "access_key": "aws_access_key_id",
        "secret_key": "aws_secret_access_key",
        "token": "aws_session_token",
    }
    for config_key, session_key in session_kwargs_map.items():
        if config_key in config:
            session_kwargs[session_key] = config.pop(config_key)

    session = get_session(**session_kwargs)

    region = config.get("region") or session.region_name

    # Check if the backend resources have been created.

    status = _get_s3_backend_status(
        session=session, region_name=region, bucket=bucket, table=dynamodb_table
    )

    if not all(status.values()):

        if any(status.values()):

            log.bad("backend: incomplete backend setup")

            account_id = get_account_id(session=session)
            bucket_arn = _get_s3_bucket_arn(region, account_id, bucket)
            table_arn = _get_dynamodb_table_arn(region, account_id, dynamodb_table)

            if status["bucket_exists"]:
                log.ok(f"backend: {bucket_arn} found")
            else:
                log.bad(f"backend: {bucket_arn} not found")

            if status["bucket_versioning_enabled"]:
                log.ok(f"backend: {bucket_arn} versioning enabled")
            else:
                log.bad(f"backend: {bucket_arn} versioning disabled")

            if status["table_exists"]:
                log.ok(f"backend: {table_arn} found")
            else:
                log.bad(f"backend: {table_arn} not found")

            raise SystemExit(1)

        _create_s3_backend(
            session=session, bucket=bucket, table=dynamodb_table, region_name=region
        )

    # Use environment variables for credentials, rather than adding
    # them to the backend configuration, because Terraform gets
    # confused when backend configuration changes, which happens
    # with certain AWS credential types such as assuming roles.

    export_environment_variables(session=session, region_name=region)

    # Return the configuration to use the backend.

    config["bucket"] = bucket
    config.setdefault("encrypt", True)
    config["dynamodb_table"] = dynamodb_table
    config["region"] = region

    return block("terraform", {"backend": {"s3": config}})
