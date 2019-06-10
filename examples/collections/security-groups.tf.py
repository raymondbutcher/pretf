from pretf.api import tf
from pretf.collections import collect


@collect
def cidr_security_group(var):

    # Inputs.
    yield tf("variable.name")
    yield tf("variable.type")
    yield tf("variable.protocol")
    yield tf("variable.cidrs", {"default": []})
    yield tf("variable.ports", {"default": []})

    group_name_lower = var.name.lower().replace("-", "_")

    # Group resource.
    group = yield tf(
        f"resource.aws_security_group.{group_name_lower}", {"name": var.name}
    )

    # Rule resources.
    for cidr in sorted(set(var.cidrs)):
        cidr_name = cidr.replace(".", "_").replace("/", "_")
        for port in var.ports:
            if var.type == "egress":
                rule_name = f"{group_name_lower}_to_{cidr_name}_{port}"
            else:
                rule_name = f"{group_name_lower}_{port}_from_{cidr_name}"
            yield tf(
                f"resource.aws_security_group_rule.{rule_name}",
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
    yield tf(f"output.group", {"value": group})


@collect
def open_egress_security_group(var):

    # Inputs.
    yield tf("variable.name", {"default": "egress"})

    # Use a nested collection for resources.
    egress = yield cidr_security_group(
        name=var.name, type="egress", cidrs=["0.0.0.0/0"], protocol="-1", ports=[0]
    )

    # Outputs.
    yield tf(f"output.group", {"value": egress.group})


def terraform(var):
    egress = yield open_egress_security_group(name="pretf-egress")

    web = yield cidr_security_group(
        name="pretf-web",
        type="ingress",
        cidrs=["10.0.0.0/24", "192.168.0.0/24"],
        protocol="tcp",
        ports=[80, 443],
    )

    yield tf("output.egress_sg_id", {"value": egress.group.id})
    yield tf("output.web_sg_id", {"value": web.group.id})
