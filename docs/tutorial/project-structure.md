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

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json and *.tfvars.json files from *.tf.py and *.tfvars.py
    # symlinks that were just created.
    create()

    # Execute Terraform.
    return execute()
```

```python
# env/stage/pretf.py

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json and *.tfvars.json files from *.tf.py and *.tfvars.py
    # symlinks that were just created.
    create()

    # Execute Terraform.
    return execute()
```

```python
# env/prod/pretf.py

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json and *.tfvars.json files from *.tf.py and *.tfvars.py
    # symlinks that were just created.
    create()

    # Execute Terraform.
    return execute()
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

## The 'mirror' function

The above code uses the `mirror()` function which creates symlinks in the current directory pointing to files and directories in other directories.

## Reuse logic

The above example contains three `pretf.py` files with the same code. One way to avoid this duplicated logic is to move it into a separate `pretf_env.py` file and use it from each `pretf.py` file in the environment directories. For example:

```python
# env/pretf_env.py

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json and *.tfvars.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json and *.tfvars.json files from *.tf.py and *.tfvars.py
    # symlinks that were just created.
    create()

    # Execute Terraform.
    return execute()
```

```python
# env/dev/pretf.py

from pretf.util import import_file


def run():
    # Call the shared run() function.
    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run()
```

```python
# env/stage/pretf.py

from pretf.util import import_file


def run():
    # Call the shared run() function.
    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run()
```

```python
# env/prod/pretf.py

from pretf.util import import_file


def run():
    # Call the shared run() function.
    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run()
```

## The 'import_file' function

The above code uses the `import_file()` context manager which imports a module from any local filesystem path. It also temporarily adds the file's directory to `sys.path` so that the imported module is able to import other modules in the same directory.
