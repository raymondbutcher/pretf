# Pretf

**Note: This is in very early development. Things are not yet implemented. The API may change as I experiment with different use-cases and try things out.**

Pretf is a completely transparent, drop-in Terraform wrapper that generates Terraform configuration with Python. It requires no configuration and no changes to standard Terraform projects to start using it.

Terraform is good at managing resources, and the configuration language HCL is sometimes quite nice, but HCL is very limited when compared to Python. Luckily, Terraform also supports configuration as JSON files. Pretf allows you to write Python code, with for-loops and everything, to output simple JSON files for Terraform.

### Features and goals

* Drop into any standard Terraform project.
  * Configuration is optional.
  * No changes are required to standard Terraform projects.
  * Standard Terraform usage.
* Super flexible.
  * Change the entire workflow if you want.
* Small codebase.
  * No concept of the hundreds or thousands of Terraform resources, just provide a generic way to create JSON for them.
* Easy to learn.
  * Takes under 5 minutes to understand all of Pretf if you're familiar with Python.

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

## Installation

```
pip install pretf
```

Requires:

* Python 3.6+
* Terraform 0.12+


## Configuration

Configuration is completely optional.

By default, Pretf will create `*.tf.json` files from any `*.tf.py` files in the current directory and then execute Terraform.

Configuration can be used to:

* Pass parameters into your Python functions.
* Load Python files from outside of the current directory.
* Clean up previously created files.
* Not run `terraform` after generating files.
* Do anything, because you configure Pretf by writing a Python function.

In the directory where you will run Pretf/Terraform, create a file named `pretf.py`:

```python
from pretf import create, execute, remove


def run():

    params = {"aws_region": "eu-west-1", "envname": "prod", "envtype": "prod"}

    created = create("../src", **params)

    remove("*.tf.json", exclude=created)

    execute("terraform", default_args=["validate"])
```

If Pretf finds a `pretf.py` file with a `run()` function, it will call that instead of performing its default behaviour.

This function can be adjusted to suit your project. Pretf exposes a small number functions designed to be used here, but there is nothing stopping you from importing other libraries or adding your own custom functionality.

## Project background

I have spent over 2 years building and supporting infrastructure with Terraform. Terraform regularly forces me write code that is ugly and unintuitive. Some things are impossible without calling external scripts, or using wrappers like [Jinjaform](https://github.com/claranet/jinjaform).

Jinjaform has been successful in some respects. It has made some mostly impossible tasks possible. However, the mixture of Jinja2 templates and HCL is ugly. In an attempt to make those templates cleaner, support for custom Jinja2 filters and functions (written in Python) was added. So now Jinjaform mixes HCL, Jinja2 and Python. Pretf is the next step, just getting out of the way and letting you write some Python code.
