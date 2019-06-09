## collect

This is a decorator used to create a collection. Collections are similar to Terraform modules except the resources are included in the root module rather than under a named module.
    
Decorated functions should:

* Accept a single argument `var`
* Yield `pretf.api.tf` blocks
    * Optionally including `variable` blocks to define inputs
    * Optionally including `output` blocks to define outputs

When using a collection, any required inputs defined by variable blocks must be passed in as keyword arguments. Any outputs defined by output blocks can be accessed as attributes of the collection.

Example:

```python
# security-groups.tf.py

from pretf.api import tf
from pretf.collections import collect


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
    web = yield security_group(
        name="web",
        type="ingress",
        cidrs=["10.0.0.0/24", "192.168.0.0/24"],
        protocol="tcp",
        ports=[80, 443],
    )
    yield tf("output.web_sg_id", {"value": web.group.id})
```
