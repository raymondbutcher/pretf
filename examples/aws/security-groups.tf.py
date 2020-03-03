from ipaddress import IPv4Network

from pretf.blocks import output, resource


def pretf_blocks(var):

    private_label = "private"
    private = yield resource.aws_security_group[private_label](
        name="pretf-example-aws-private",
    )

    public_label = "public"
    public = yield resource.aws_security_group[public_label](
        name="pretf-example-aws-public",
    )

    for cidr in sorted(set(var.security_group_allowed_cidrs)):

        cidr_label = cidr.replace(".", "_").replace("/", "_")

        if IPv4Network(cidr).is_global:
            group = public
            group_label = public_label
        else:
            group = private
            group_label = private_label

        for port in (80, 443):
            rule_label = f"{group_label}_{port}_from_{cidr_label}"
            yield resource.aws_security_group_rule[rule_label](
                security_group_id=group.id,
                type="ingress",
                protocol="tcp",
                from_port=port,
                to_port=port,
                cidr_blocks=[cidr],
            )

    yield output.private_sg_id(value=private.id)
    yield output.public_sg_id(value=public.id)
