from pretf.api import tf
from pretf.collections import collect


@collect
def open_egress_security_group(var):

    # Inputs.
    yield tf("variable.name", {"default": "egress"})

    # Use a nested collection for resources.
    egress = yield security_group(
        name=var.name, type="egress", cidrs=["0.0.0.0/0"], protocol="-1", ports=[0]
    )

    # Outputs.
    yield tf(f"output.group", {"value": egress.group})


@collect
def security_group(var):

    # Inputs.
    yield tf("variable.name")
    yield tf("variable.type")
    yield tf("variable.protocol")
    yield tf("variable.cidrs", {"default": []})
    yield tf("variable.ports", {"default": []})

    # Group resource.
    group = yield tf(f"resource.aws_security_group.{var.name}", {"name": var.name})

    # Rule resources.
    for cidr in sorted(set(var.cidrs)):
        cidr_label = cidr.replace(".", "_").replace("/", "_")
        for port in var.ports:
            rule_label = f"{var.name}_{port}_from_{cidr_label}"
            yield tf(
                f"resource.aws_security_group_rule.{rule_label}",
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


def terraform(var):
    egress = yield open_egress_security_group()

    web = yield security_group(
        name="web",
        type="ingress",
        cidrs=["10.0.0.0/24", "192.168.0.0/24"],
        protocol="tcp",
        ports=[80, 443],
    )

    yield tf("output.egress_sg_id", {"value": egress.group.id})
    yield tf("output.web_sg_id", {"value": web.group.id})
