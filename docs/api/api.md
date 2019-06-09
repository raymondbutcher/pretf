## create

Creates `*.tf.json` and `*.tfvars.json` files in the current directory from `*.tf.py` and `*.tfvars.py` files in the source directories.

Uses the current directory as a source directory if none are specified. If multiple directories are specified, and there are duplicate file names, the files in the latter directories take precedence.

It is recommended to call create() only once. Pass in multiple source_dirs rather than calling it multiple times. Pretf parses variables from files in the current directory and the source_dirs. Calling it multiple times with different source_dirs could give Pretf a different set of files to parse each time it is called, resulting in different variables each time.

Signature:

```python
create(*source_dirs)

source_dirs:
    optional sequence of directories to use for source files

returns:
    list(pathlib.Path) of created files
```

Example:

```python
from pretf.api import create


def run():
    create()
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
from pretf.api import execute


def run():
    return execute()
```

## log.accept

Prompts the user to enter "yes" or "no". Returns `True` if the response was "yes", otherwise `False`. Pressing Ctrl-C counts as "no".

Signature:

```python
log.accept(message)

message:
    required str

returns:
    bool
```

Example:

```python
from pretf.api import log


def run():
    if log.accept("do you wish to continue?"):
        print("user accepted the prompt")
    else:
        print("user did not accept the prompt")
```

## log.bad

Displays a message prefixed with `[pref]` in red.

Signature:

```python
log.bad(message)

message:
    required str

returns:
    None
```

Example:

```python
from pretf.api import log


def run():
    log.bad("something bad happened")
```

## log.ok

Displays a message prefixed with `[pref]` in cyan.

Signature:

```python
log.ok(message)

message:
    required str

returns:
    None
```

Example:

```python
from pretf.api import log


def run():
    log.bad("something normal happened")
```

## mirror

Creates symlinks from all files and directories in the source directories into the current directory. Deletes all existing symlinks in the current directory.

Signature:

```python
mirror(*source_dirs, exclude=["__pycache__"])

source_dirs:
    required str sequence of directories to mirror into the current directory
exclude:
    optional list of file names to exclude

returns:
    list(pathlib.Path) of created symlinks
```

Example:

```python
from pretf.api import mirror


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
from pretf.api import remove


def run():
    remove()
```

## tf

This is used to create Terraform configuration blocks from within `terraform()` functions in `*.tf.py` files. Blocks must be yielded to be included in the generated JSON files.

Signature:

```python
tf(path, body=None)

path:
    required str
body:
    optional dict

returns:
    Block
```

Example:

```python
from pretf.api import tf


def terraform(var):

    # The group resource is defined in another file,
    # but we want to reference it here, so we can
    # create a block without a body. We don't yield
    # it so it won't be included in the JSON.
    group = tf("resource.aws_iam_group.example")

    # Create and yield a block to include it in the JSON.
    user = yield tf(f"resource.aws_iam_user.example", {
        "name": "example",
    })

    # Create and yield another block, this time demonstrating
    # how block attributes can be accessed. The resulting JSON
    # will contain Terraform references like:
    #   "users": "${aws_iam_user.example.name}",
    #   "groups": ["${aws_iam_group.example.name}"]
    yield tf("resource.aws_iam_user_group_membership.example", {
        "user": user.name,
        "groups": [group.name]
    })
```
