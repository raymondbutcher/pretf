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
    stage/
      pretf.py
    prod/
      pretf.py
  src/
    *.tf
    *.tf.py
```

Code:

```python
# env/dev/pretf.py

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # passing parameters into the terraform() functions.
    create(
        animals=["dog", "cat", "buffalo", "rabbit", "badger"],
        users=["ray", "violet"],
    )

    # Execute Terraform.
    return execute()
```

```python
# env/stage/pretf.py

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # passing parameters into the terraform() functions.
    create(
        animals=["dog", "cat", "buffalo"],
        users=["ray", "violet"],
    )

    # Execute Terraform.
    return execute()
```

```python
# env/prod/pretf.py

from pretf.run import create, execute, mirror, remove


def run():
    # Delete *.tf.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # passing parameters into the terraform() functions.
    created = tf.create(
        animals=["dog", "cat"],
        users=["ray"],
    )

    # Execute Terraform.
    return execute()
```

```ini
# .gitignore

# Ignore everything in the env directories except for pretf.py
# because Pretf and Terraform create symlinks, *.tf.json files,
# backend state files, etc.
terraform/env/*/*
!terraform/env/*/pretf.py
```

## The 'mirror' function

The above code uses the `mirror()` function which creates symlinks in the current directory pointing to files and directories in other directories.

## Reuse logic

The above example contains three `pretf.py` files with the same code. One way to avoid this duplicated logic is to move it into a separate `pretf_env.py` file, import it from each `pretf.py` file, and pass in any relevant parameters. For example:

```python
# env/pretf_env.py

from pretf.run import create, execute, mirror, remove


def run_with_params(**params):
    # Delete *.tf.json files.
    remove()

    # Create symlinks in the current directory to everything in ../../src
    # This deletes any other symlinks in the current directory.
    mirror("../../src")

    # Create *.tf.json files from *.tf.py symlinks that were just created,
    # passing parameters into the terraform() functions.
    create(**params)

    # Execute Terraform.
    return execute()
```

```python
# env/dev/pretf.py

from pretf.util import import_file


def run():
    """
    Calls the shared run_with_params() function with environment-specific parameters.

    """

    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run_with_params(
            animals=["dog", "cat", "buffalo", "rabbit", "badger"],
            users=["ray", "violet"],
        )
```

```python
# env/stage/pretf.py

from pretf.util import import_file


def run():
    """
    Calls the shared run_with_params() function with environment-specific parameters.

    """

    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run_with_params(
            animals=["dog", "cat", "buffalo"],
            users=["ray", "violet"],
        )
```

```python
# env/prod/pretf.py

from pretf.util import import_file


def run():
    """
    Calls the shared run_with_params() function with environment-specific parameters.

    """

    with import_file("../pretf_env.py") as pretf_env:
        pretf_env.run_with_params(
            animals=["dog", "cat"],
            users=["ray"],
        )
```

## The 'import_file' function

The above code uses the `import_file()` context manager which imports a module from any local filesystem path. It also temporarily adds the file's directory to `sys.path` so that the imported module is able to import other modules in the same directory.

## Parameter files

It might make sense in your project to define parameters in a separate `.json` or `.yaml` files. This would result in further separation of data and code. For example:

```shell
terraform/
  env/
    dev/
      params.json
      pretf.py
    stage/
      params.json
      pretf.py
    prod/
      params.json
      pretf.py
  src/
    *.tf
    *.tf.py
```

or:

```shell
terraform/
  env/
    dev/
      pretf.py
    stage/
      pretf.py
    prod/
      pretf.py
  params/
    dev.json
    stage.json
    prod.json
  src/
    *.tf
    *.tf.py
```

Because this all happens in Python, you are not limited to those file types. You could access a database, HTTP API, anything.
