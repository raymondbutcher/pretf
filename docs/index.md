# Pretf

Pretf is a completely transparent, drop-in Terraform wrapper that generates Terraform configuration with Python. It requires no configuration and no changes to standard Terraform projects to start using it.

Terraform includes first-class support for configuration in JSON files. Pretf generates those JSON files using your Python functions.

## Requirements

* Python 3.6+
* Terraform 0.12.0+

## Installation

For core functionality:

```shell
pip install pretf
```

For AWS functionality:

```shell
pip install pretf.aws
```

Install them both:

```shell
pip install pretf[aws]
```

## Overview

Here is what happens when you run `pretf`:

1. It deletes `*.tf.json` and `*.tfvars.json` files from the current directory.
1. It creates `*.tf.json` and `*.tfvars.json` files from `*.tf.py` and `*.tfvars.py` files in the current directory.
1. It executes `terraform`, passing along any provided command line arguments.

For example, with `iam.tf.py`:

```python
from pretf.api import block


def pretf_blocks(var):

    group = yield block("resource", "aws_iam_group", "admins", {
        "name": "admins",
    })

    for name in var.admin_user_names:

        user = yield block("resource", "aws_iam_user", name, {
            "name": name,
        })

        yield block("resource", "aws_iam_user_group_membership", name, {
            "user": user.name,
            "groups": [
                group.name,
            ],
        })
```

It would generate `iam.tf.json`:

```json
[
  {
    "resource": {
      "aws_iam_group": {
        "admins": {
          "name": "admins"
        }
      }
    }
  },
  {
    "resource": {
      "aws_iam_user": {
        "ray": {
          "name": "ray"
        }
      }
    }
  },
  {
    "resource": {
      "aws_iam_user_group_membership": {
        "ray": {
          "user": "${aws_iam_user.ray.name}",
          "groups": [
            "${aws_iam_group.admins.name}"
          ]
        }
      }
    }
  },
  {
    "resource": {
      "aws_iam_user": {
        "violet": {
          "name": "violet"
        }
      }
    }
  },
  {
    "resource": {
      "aws_iam_user_group_membership": {
        "violet": {
          "user": "${aws_iam_user.violet.name}",
          "groups": [
            "${aws_iam_group.admins.name}"
          ]
        }
      }
    }
  }
]
```

And then Terraform would manage those resources.

## Configuration

Configuration is completely optional. By default, Pretf will delete `*.tf.json` and `*.tfvars.json` files, create `*.tf.json` and `*.tfvars.json` files from `*.tf.py` and `*.tfvars.py` files, and then execute Terraform.

To make something else to happen when Pretf runs, simply create a `pretf.workflow.py` file containing a `pretf_workflow()` function. This could include:

* Using files from outside of the current directory.
* Not running `terraform` after generating files.
* Doing anything, because you configure Pretf by writing a Python function.

## Source code

The source code for Pretf is located at: [https://github.com/raymondbutcher/pretf](https://github.com/raymondbutcher/pretf)
