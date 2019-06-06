## create

Creates `*.tf.json` and `*.tfvars.json` files from `*.tf.py` and `*.tfvars.py` files.

Signature:

```python
create()

returns:
    list(pathlib.Path) of created files
```

Example:

```python
from pretf.run import create


def run():
    create(env="dev")
```

## execute

Executes Terraform and waits for it to finish. Command line arguments are passed through to Terraform. Returns the exit code from Terraform.

Signature:

```python
execute(verbose=True)

verbose:
    optional bool for whether to log the command

returns:
    int exit code from process
```

Example:

```python
from pretf.run import execute


def run():
    return execute()
```

## mirror

Creates symlinks from all files and directories in the source directories into the target directory. Deletes all existing symlinks in the target directory.

Signature:

```python
mirror(*sources, target=".", exclude=["__pycache__"])

sources:
    required str sequence of directories to mirror into the target directory
target:
    optional str of where to create the symlinks
exclude:
    optional list of file names to exclude

returns:
    list(pathlib.Path) of created symlinks
```

Example:

```python
from pretf.run import mirror


def run():
    mirror("../src")
```

## remove

Deletes all `*.tf.json` and `*.tfvars.json` files in the current directory. Optionally exclude specific files from being deleted.

Signature:

```python
remove(exclude=None)

exclude:
    optional str or list of str of file names to keep

returns:
    list(pathlib.Path) of deleted files
```

Example:

```python
from pretf.run import remove


def run():
    remove()
```
