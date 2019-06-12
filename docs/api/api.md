## create

Creates `*.tf.json` and `*.tfvars.json` files in the current directory from `*.tf.py` and `*.tfvars.py` files in the source directories.

Uses the current directory as a source directory if none are specified. If multiple directories are specified, and there are duplicate file names, the files in the latter directories take precedence.

It is recommended to call create() only once. Pass in multiple source_dirs rather than calling it multiple times. Pretf parses variables from files in the current directory and the source_dirs. Calling it multiple times with different source_dirs could give Pretf a different set of files to parse each time it is called, resulting in different variables each time.

Signature:

```python
def create(*source_dirs: Union[Path, str]) -> List[Path]:

source_dirs:
    directories to use for source files

returns:
    created files
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
def execute(verbose:bool=True) -> int:

verbose:
    whether to print the command

returns:
    exit code from process
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

Creates symlinks from all files and directories matching the source patterns into the current directory. Deletes all pre-existing symlinks in the current directory.

Signature:

```python
def mirror(
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [".*", "_*"],
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    path glob patterns to mirror into the current directory
exclude_name_patterns:
    name glob patterns to exclude
cwd:
    current directory
verbose:
    whether to print information

returns:
    created symlinks
```

Example:

```python
from pretf.api import mirror


def run():
    mirror("../src/*")
```

## remove

Deletes matching files from the current directory. Defaults to deleting files normally created by the `create()` function. Optionally exclude files matching a specified pattern.

Signature:

```python
def remove(
    path_patterns: Sequence[str] = ["*.tf.json", "*.tfvars.json"],
    exclude_name_patterns: Sequence[str] = [],
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:

path_patterns:
    path glob patterns to mirror into the current directory
exclude_name_patterns:
    name glob patterns to exclude
cwd:
    current directory
verbose:
    whether to print information

returns:
    removed files
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
