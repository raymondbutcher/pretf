from argparse import Namespace


def create_s3_backend(bucket, dynamodb_table, region=None, encrypt=True):
    # Prompt to create the bucket/table if they don't exist.
    # Maybe use cloudformation?
    return Namespace(
        bucket='TODO',
        dynamodb_table='TODO',
        encrypt=encrypt,
        region='TODO',
    )


def export_credentials(**kwargs):
    pass
