from pretf import aws, tf


def main(aws_region, envtype, **kwargs):

    return # disabled until create_s3_backend() implemented

    backend_name = f'customer-tfstate-{envtype}'

    backend = aws.create_s3_backend(
        region=aws_region,
        bucket=backend_name,
        dynamodb_table=backend_name,
        encrypt=True,
    )

    yield tf('terraform', {
        'backend': {
            's3': {
                'region': backend.region,
                'bucket': backend.bucket,
                'dynamodb_table': backend.dynamodb_table,
                'encrypt': backend.encrypt,
                'key': 'terraform.tfstate',
            },
        },
        'required_version': '0.12.0',
    })
