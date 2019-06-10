from pretf.api import tf


def terraform(var):

    group = yield tf("resource.aws_iam_group.pretf", {"name": "pretf-iam-users"})

    for name in var.user_names:

        name_lower = name.lower().replace("-", "_")

        user = yield tf(f"resource.aws_iam_user.{name_lower}", {"name": name})

        yield tf(
            f"resource.aws_iam_user_group_membership.{name_lower}",
            {"user": user.name, "groups": [group.name]},
        )
