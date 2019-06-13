from pretf.api import block
from pretf.collections import collect


def pretf_blocks(var):
    egress = yield open_egress_security_group(name="pretf-egress")

    web = yield cidr_security_group(
        name="pretf-web",
        type="ingress",
        cidrs=["10.0.0.0/24", "192.168.0.0/24"],
        protocol="tcp",
        ports=[80, 443],
    )

    yield block("output", "egress_sg_id", {"value": egress.group.id})
    yield block("output", "web_sg_id", {"value": web.group.id})


@collect
def cidr_security_group(var):

    # Inputs.
    yield block("variable", "name", {})
    yield block("variable", "type", {})
    yield block("variable", "protocol", {})
    yield block("variable", "cidrs", {"default": []})
    yield block("variable", "ports", {"default": []})

    group_label = var.name.lower().replace("-", "_")

    # Group resource.
    group = yield block(
        "resource", "aws_security_group", group_label, {"name": var.name}
    )

    # Rule resources.
    for cidr in sorted(set(var.cidrs)):
        cidr_name = cidr.replace(".", "_").replace("/", "_")
        for port in var.ports:
            if var.type == "egress":
                rule_label = f"{group_label}_to_{cidr_name}_{port}"
            else:
                rule_label = f"{group_label}_{port}_from_{cidr_name}"
            yield block(
                "resource",
                "aws_security_group_rule",
                rule_label,
                {
                    "security_group_id": group.id,
                    "type": "ingress",
                    "protocol": var.protocol,
                    "from_port": port,
                    "to_port": port,
                    "cidr_blocks": [cidr],
                },
            )

    # Outputs.
    yield block("output", "group", {"value": group})


@collect
def open_egress_security_group(var):

    # Inputs.
    yield block("variable", "name", {"default": "egress"})

    # Use a nested collection for resources.
    egress = yield cidr_security_group(
        name=var.name, type="egress", cidrs=["0.0.0.0/0"], protocol="-1", ports=[0]
    )

    # Outputs.
    yield block("output", "group", {"value": egress.group})
