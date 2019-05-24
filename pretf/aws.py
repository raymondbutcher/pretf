from argparse import Namespace


def create_s3_backend(bucket, dynamodb_table, region=None, encrypt=True):
    # Prompt to create the bucket/table if they don't exist.
    # Maybe use cloudformation?
    return Namespace(
        bucket=bucket, dynamodb_table=dynamodb_table, encrypt=encrypt, region=region
    )


def export_credentials(**kwargs):
    pass
