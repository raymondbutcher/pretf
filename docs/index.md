# Pretf

Pretf is a completely transparent, drop-in Terraform wrapper that generates Terraform configuration with Python. It requires no configuration and no changes to standard Terraform projects to start using it.

Terraform is good at managing resources, and the configuration language HCL is sometimes quite nice, but HCL is very limited when compared to Python. Luckily, Terraform also supports configuration as JSON files. Pretf allows you to write Python code, with for-loops and everything, to output simple JSON files for Terraform.

## Requirements

* Python 3.6+
* Terraform 0.12.0+

## Installation

For core functionality:

```shell
pip install pretf
```

For extensions:

```shell
pip install pretf.aws
```

## Overview

Here is what happens when you run `pretf`:

1. It finds `*.tf.py` files in the current directory and creates `*.tf.json` files.
1. It executes `terraform`, passing along any provided command line arguments.

For example, with `iam.tf.py`:

```python
from pretf.core import tf


def terraform():

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

Configuration is completely optional. By default, Pretf will create `*.tf.json` files from any `*.tf.py` files found in the current directory and then execute Terraform.

If you want something else to happen when Pretf runs, simply create a `pretf.py` file with your own `run()` function. This could include:

* Passing parameters into your Python functions.
* Using files from outside of the current directory.
* Cleaning up previously created files.
* Not running `terraform` after generating files.
* Doing anything, because you configure Pretf by writing a Python function.

## Source code

The source code for Pretf is located at: [https://github.com/raymondbutcher/pretf](https://github.com/raymondbutcher/pretf)
