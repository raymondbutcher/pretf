So far, we have seen how Pretf can be used in a single directory. This is fine for some projects, but many projects would benefit from using multiple directories. Pretf does not dictate any particular project structure, but it is worth discussing and considering them.

Some projects use a single directory to manage multiple environments, using wrapper scripts to take command line arguments, dynamically set and initialize the backend, and use the appropriate variables file. This is not very efficient, as `terraform init` must be run whenever switching between environments (or more likely every single time because it is hard to determine whether it actually needs to run). Additionally, the command line arguments to specify the environment is often not obvious, requiring one to read documentation or source code to remember how and where to deploy their changes.

## One directory per backend

Features:

* Self-documenting. List the directories to see all of the environments.
* Easy to use. Navigate into the relevant environment directory and use the commands `init`, `plan`, `apply`, etc.
* Terraform state files are persistent. Even when using a remote backend, Terraform keeps local files that reference it. There is no need to initialize the backend more than once, to switch between backends.

Structure:

```shell
terraform/
  env/
    dev/
      pretf.py
      terraform.tfvars
    stage/
      pretf.py
      terraform.tfvars
    prod/
      pretf.py
      terraform.tfvars
  src/
    *.tf
    *.tf.py
```

Code:

```python
# env/dev/pretf.py

from pretf import workflow


def pretf_workflow():
    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    workflow.mirror_files("../../src/*")

    # Run the standard Pretf workflow to create files and execute Terraform.
    return workflow.default()
```

```python
# env/stage/pretf.py

from pretf import workflow


def pretf_workflow():
    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    workflow.mirror_files("../../src/*")

    # Run the standard Pretf workflow to create files and execute Terraform.
    return workflow.default()
```

```python
# env/prod/pretf.py

from pretf import workflow


def pretf_workflow():
    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    workflow.mirror_files("../../src/*")

    # Run the standard Pretf workflow to create files and execute Terraform.
    return workflow.default()
```

```ini
# .gitignore

# Ignore everything in the env directories except for pretf.py
# and terraform.tfvars because Pretf and Terraform create symlinks,
# *.tf.json files, backend state files, etc.
terraform/env/*/*
!terraform/env/*/pretf.py
!terraform/env/*/terraform.tfvars
```

## Reuse logic

The above example contains three `pretf.py` files with the same code. Workflows could potentially contain more code than the above examples, and each `pretf.py` file would look identical or very similar. One way to avoid this duplicated logic is to move it into a separate `pretf_workflow.py` file and call it from each `pretf.py` file in the environment directories. The name `pretf_workflow.py` is used, rather than `pretf.py`, so that Pretf does not automatically run it. For example:

```python
# env/pretf_workflow.py

from pretf import workflow


def pretf_workflow():
    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    workflow.mirror_files("../src/*")

    # Run the standard Pretf workflow to create files and execute Terraform.
    return workflow.default()
```

```python
# env/dev/pretf.py

from pretf import workflow


def pretf_workflow():
    return workflow.custom("../pretf_workflow.py")
```

```python
# env/stage/pretf.py

from pretf import workflow


def pretf_workflow():
    return workflow.custom("../pretf_workflow.py")
```

```python
# env/prod/pretf.py

from pretf import workflow


def pretf_workflow():
    return workflow.custom("../pretf_workflow.py")
```

## The 'workflow.custom()' function

The above code uses the `workflow.custom()` function which imports a module from any local filesystem path and calls the `pretf_workflow()` function. This function can be found in the API documentation.
