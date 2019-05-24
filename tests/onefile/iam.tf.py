from pretf import tf


def main(params):

    group = yield tf('resource.aws_iam_group.admins', {
        'name': 'admins',
    })

    for username in params.users:

        user = yield tf(f'resource.aws_iam_user.{username}', {
            'name': username,
        })

        yield tf(f'resource.aws_iam_user_group_membership.{username}', {
            'user': user.name,
            'groups': [
                group.name,
            ],
        })
