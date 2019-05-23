import json

from pretf import tf, register_file


@register_file('main.json')
def main_resources(params):

    name = f'pretf-test-{params.envname}'

    bucket = yield tf('resource.aws_s3_bucket.test', {
        'bucket': name,
        'acl': 'private',
        'server_side_encryption_configuration': {
            'rule': {
                'apply_server_side_encryption_by_default': {
                    'sse_algorithm': 'AES256',
                },
            },
        },
    })

    policy = yield tf('data.aws_iam_policy_document.lambda', {
        'statement': {
            'effect': 'Allow',
            'actions': [
                's3:ListBucket',
                's3:PutObject',
            ],
            'resources': [
                bucket.arn,
                f'{bucket.arn}/*',
            ],
        }
    })

    yield tf('module.lambda', {
        'source': 'github.com/claranet/terraform-aws-lambda?ref=v0.12.0',
        'description': 'Test',
        'function_name': name,
        'handler': 'main.lambda_handler',
        'runtime': 'python3.7',
        'source_path': '../src/lambda',
        'attach_policy': True,
        'policy': policy.json,
        'environment': {
            'variables': {
                'BUCKET': bucket.id,
                'DATA': json.dumps(params.data),
            },
        },
    })

    # Create dynamic resources
    for i in range(5):
        yield tf(f'module.thing_{i}', {
            'source': './modules/thing',
        })
