Pretf finds and imports Python files from the current directory. Pretf calls specific functions in those files. This page explains the files and functions that you must have in your project for Pretf to work.

## \*.tf.py

By default, Pretf looks for `*.tf.py` files and creates matching `*.tf.json` files. For example, a file named `iam.tf.py` would create `iam.tf.json`.

These files must contain a `pretf_blocks()` function. This function can optionally accept any of the arguments `path`, `terraform` and `var`, which provide access to the same values as in Terraform. This function must be a generator that yields only blocks and/or dictionaries representing Terraform blocks.

Example:

```python
# iam.tf.py

from pretf.api import block


def pretf_blocks(var):
    for user_name in var.user_names:

        yield block("resource", "aws_iam_user", user_name, {
            "name": user_name,
        })

        label = f"{user_name}_in_{var.group_name}"
        yield block("resource", "aws_iam_user_group_membership",label, {
            "user": user.name,
            "groups": [var.group_name],
        })
```

## \*.tfvars.py

By default, Pretf looks for `*.tfvars.py` files and creates matching `*.tfvars.json` files. For example, a file named `terraform.tfvars.py` would create `terraform.tfvars.json`.

These files must contain a `pretf_variables()` function. This function can optionally accept any of the arguments `path`, `terraform` and `var`, which provide access to the same values as in Terraform. This function must be a generator that yields dictionaries containing variable values. Each dictionary can contain any number of variables.

Example:

```python
# terraform.tfvars.py


def pretf_variables():
    yield {"environment": "dev"}
    yield {
        "group_name": "admin",
        "user_names": ["peanut", "cornelius"],
    }
```

## pretf.workflow.py

When Pretf runs, it looks for `pretf.workflow.py` in the current directory. If it exists, it will call the `pretf_workflow()`. This function can optionally accept any of the arguments `path` and `terraform` which provide access to the same values as in Terraform. If this file does not exist, then Pretf runs in default mode.

The following is a valid `pretf.workflow.py` file that implements performs the same functionality as default mode. It can be extended with custom logic. 

Example:

```python
# pretf.workflow.py

from pretf import workflow


def pretf_workflow():
    # Delete *.tf.json and *.tfvars.json files.
    workflow.delete_files()

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    workflow.create_files()

    # Execute Terraform.
    return workflow.execute_terraform()
```
