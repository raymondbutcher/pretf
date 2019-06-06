from pretf.api import tf


def terraform(var):

    group = yield tf("resource.aws_iam_group.admins", {"name": "admins"})

    for name in var.admin_user_names:

        user = yield tf(f"resource.aws_iam_user.{name}", {"name": name})

        yield tf(
            f"resource.aws_iam_user_group_membership.{name}",
            {"user": user.name, "groups": [group.name]},
        )
