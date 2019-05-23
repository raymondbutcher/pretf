from argparse import Namespace


def create_s3_backend(bucket, dynamodb_table, region=None, encrypt=True):
    return Namespace(
        bucket='TODO',
        dynamodb_table='TODO',
        encrypt=encrypt,
        region='TODO',
    )


def export_credentials(**kwargs):
    pass
