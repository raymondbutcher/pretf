from pretf.api import block


def pretf_blocks(var):

    group = yield block(
        "resource", "aws_iam_group", "pretf", {"name": "pretf-iam-users"}
    )

    for name in var.user_names:

        name_label = name.lower().replace("-", "_")

        user = yield block("resource", "aws_iam_user", name_label, {"name": name})

        yield block(
            "resource",
            "aws_iam_user_group_membership",
            name_label,
            {"user": user.name, "groups": [group.name]},
        )
