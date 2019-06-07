Pretf finds and imports Python files from the current directory. Pretf calls specific functions in those files. This page explains the files and functions that you must have in your project for Pretf to work.

## \*.tf.py and \*.tfvars.py

By default, Pretf looks for `*.tf.py` and `*.tfvars.py` files and creates matching `*.tf.json` and `*.tfvars.json` files respectively. For example, a file named `iam.tf.py` would create `iam.tf.json`, and `terraform.tfvars.py` would create `terraform.tfvars.json`.

These files must contain a `terraform` function. This function must accept a single argument `var` which provides access to Terraform variables. This function must be a generator that yields only `tf` objects and/or dictionaries representing Terraform blocks.

Example:

```python
# iam.tf.py

from pretf.api import tf


def terraform(var):
    yield tf(f"resource.aws_iam_user.peanut", {
        "name": "peanut",
    })

    yield tf(f"resource.aws_iam_user.cornelius", {
        "name": "cornelius",
    })
```

## pretf.py

When Pretf runs, it looks for `pretf.py` in the current directory. If it exists, it will call the `run` function without any arguments. If it does not exist, then Pretf runs in default mode.

The following is a valid `pretf.py` file that implements performs the same functionality as default mode. It can be extended with custom logic. 

Example:

```python
# pretf.py

from pretf.api import create, execute, remove


def run():
    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    create()

    # Execute Terraform.
    return execute()
```
