# Pretf

Pretf is a completely transparent, drop-in Terraform wrapper that generates Terraform configuration with Python. It requires no configuration and no changes to standard Terraform projects to start using it.

Terraform is good at managing resources, and the configuration language HCL is quite nice, but HCL is very limited when compared to Python. Luckily, Terraform also supports configuration as JSON files. Pretf allows you to write Python code, with for-loops and everything, to output simple JSON files for Terraform.

## Overview

Here is what happens when you run `pretf`:

1. It finds `*.tf.py` files in the current directory and creates `*.tf.json` files.
1. It exeutes `terraform`, passing along any provided command line arguments.

For example, with `iam.tf.py`:

```python
from pretf import tf


def main():

    group = yield tf('resource.aws_iam_group.admins', {
        'name': 'admins',
    })

    user_names = [
        'ray',
        'violet',
    ]

    for name in user_names:

        user = yield tf(f'resource.aws_iam_user.{name}', {
            'name': name,
        })

        yield tf(f'resource.aws_iam_user_group_membership.{name}', {
            'user': user.name,
            'groups': [
                group.name,
            ],
        })
```

It would generate `iam.tf.json`:

```json
{
  "resource": {
    "aws_iam_group": {
      "admins": {
        "name": "admins"
      }
    },
    "aws_iam_user": {
      "ray": {
        "name": "ray"
      },
      "violet": {
        "name": "violet"
      }
    },
    "aws_iam_user_group_membership": {
      "ray": {
        "user": "${aws_iam_user.ray.name}",
        "groups": [
          "${aws_iam_group.admins.name}"
        ]
      },
      "violet": {
        "user": "${aws_iam_user.violet.name}",
        "groups": [
          "${aws_iam_group.admins.name}"
        ]
      }
    }
  }
}
```

And then Terraform would manage those resources.

## Configuration

Configuration is completely optional.

By default, Pretf will create `*.tf.json` files from `*.tf.py` files and then execute Terraform.

Configuration can be used to:

* Pass parameters into your Python functions.
* Load Python files from outside of the current directory.
* Clean up previously generated files.

## Project status

This is in very early development. Things are not yet implemented. The API is likely to change as I experiment with different use-cases and try things out.
