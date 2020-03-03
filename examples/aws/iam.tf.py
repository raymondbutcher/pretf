from pretf.api import labels
from pretf.blocks import output, resource


def pretf_blocks(var):

    group = yield resource.aws_iam_group.pretf(
        name="pretf-aws",
    )

    for name in var.user_names:

        name_label = labels.clean(name)

        user = yield resource.aws_iam_user[name_label](
            name=name,
        )

        yield resource.aws_iam_user_group_membership[name_label](
            user=user.name,
            groups=[group.name],
        )

        yield output[f"user_{name_label}"](
            value=user.name,
        )
