import json
import os
from collections import namedtuple
from functools import lru_cache
from time import sleep

import boto_source_profile_mfa

from pretf import log, tf


def _create_s3_backend(session, bucket, table, region):

    # Prompt before creating anything.
    account_id = get_account_id(session)
    bucket_arn = _get_s3_bucket_arn(region, account_id, bucket)
    table_arn = _get_dynamodb_table_arn(region, account_id, table)
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
    stack_arn = _get_cloudformation_stack_arn(region, account_id, stack_name)
    log.ok(f"backend: creating {stack_arn}")

    # Create the stack.
    cloudformation_client = session.client("cloudformation")
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


def _get_cloudformation_stack_arn(region, account_id, stack_name):
    return f"arn:aws:cloudformation:{region}:{account_id}:stack/{stack_name}"


def _get_dynamodb_table_arn(region, account_id, table):
    return f"arn:aws:dynamodb:{region}:{account_id}:{table}"


def _get_s3_bucket_arn(region, account_id, bucket):
    return f"arn:aws:s3:{region}:{account_id}:{bucket}"


def _get_s3_backend_status(session, region, bucket, table):

    s3_client = session.client("s3")

    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket)
    except s3_client.exceptions.NoSuchBucket:
        bucket_exists = False
        bucket_versioning_enabled = False
    else:
        bucket_exists = True
        bucket_versioning_enabled = response["Status"] == "Enabled"

    dynamodb_client = session.client("dynamodb", region_name=region)

    try:
        dynamodb_client.describe_table(TableName=table)
    except dynamodb_client.exceptions.ResourceNotFoundException:
        table_exists = False
    else:
        table_exists = True

    return {
        'bucket_exists': bucket_exists,
        'bucket_versioning_enabled': bucket_versioning_enabled,
        'table_exists': table_exists,
    }


@lru_cache()
def get_account_id(session=None, **kwargs):
    if session is None:
        session = get_session(**kwargs)
    sts_client = session.client("sts")
    account_id = sts_client.get_caller_identity()["Account"]
    return account_id


def get_frozen_credentials(session=None, **kwargs):
    if session is None:
        session = get_session(**kwargs)
    return session.get_credentials().get_frozen_credentials()


@lru_cache()
def get_session(**kwargs):
    return boto_source_profile_mfa.get_session(**kwargs)


def s3_backend(session, bucket, key, table, region=None):
    """
    This ensures that the S3 backend exists, prompting to create it
    if necessary, sets the credentials as environment variables,
    then returns a Terraform configuration block for it.

    """

    if not region:
        region = session.region_name

    # Check if the backend resources have been created.

    status = _get_s3_backend_status(
        session=session, region=region, bucket=bucket, table=table
    )

    if not all(status.values()):

        if any(status.values()):

            log.bad("backend: incomplete backend setup")

            account_id = get_account_id(session=session)
            bucket_arn = _get_s3_bucket_arn(region, account_id, bucket)
            table_arn = _get_dynamodb_table_arn(region, account_id, table)

            if status['bucket_exists']:
                log.ok(f"backend: {bucket_arn} found")
            else:
                log.bad(f"backend: {bucket_arn} not found")

            if status['bucket_versioning_enabled']:
                log.ok(f"backend: {bucket_arn} versioning enabled")
            else:
                log.bad(f"backend: {bucket_arn} versioning disabled")

            if status['table_exists']:
                log.ok(f"backend: {table_arn} found")
            else:
                log.bad(f"backend: {table_arn} not found")

            raise SystemExit(1)

        _create_s3_backend(session=session, bucket=bucket, table=table, region=region)

    # Use environment variables for credentials, rather than adding
    # them to the backend configuration, because Terraform gets
    # confused when backend configuration changes.

    os.environ["AWS_REGION"] = region
    os.environ["AWS_DEFAULT_REGION"] = region

    creds = session.get_credentials().get_frozen_credentials()

    if creds.access_key:
        os.environ["AWS_ACCESS_KEY_ID"] = creds.access_key

    if creds.secret_key:
        os.environ["AWS_SECRET_ACCESS_KEY"] = creds.secret_key

    if creds.token:
        os.environ["AWS_SECURITY_TOKEN"] = creds.token
        os.environ["AWS_SESSION_TOKEN"] = creds.token

    # Return the configuration to use the backend.

    return tf(
        "terraform",
        {
            "backend": {
                "s3": {
                    "region": region,
                    "bucket": bucket,
                    "dynamodb_table": table,
                    "encrypt": True,
                    "key": "terraform.tfstate",
                }
            }
        },
    )
