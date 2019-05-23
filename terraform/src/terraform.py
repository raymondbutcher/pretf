from pretf import aws, tf, register_file


@register_file('terraform.json')
def terraform_block(params):

    backend_name = f'customer-tfstate-{params.envtype}'

    # This will prompt to create the bucket/table if they don't exist.
    # Try to use cloudformation?
    backend = aws.create_s3_backend(
        region=params.region,
        bucket=backend_name,
        dynamodb_table=backend_name,
        encrypt=True,
    )

    yield tf('terraform', {
        'backend.s3': {
            'region': backend.region,
            'bucket': backend.bucket,
            'dynamodb_table': backend.dynamodb_table,
            'encrypt': backend.encrypt,
            'key': 'terraform.tfstate',
        },
        'required_version': '0.11.11',
    })
