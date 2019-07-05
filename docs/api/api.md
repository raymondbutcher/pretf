## block

This is used to create Terraform configuration blocks from within `pretf_blocks()` functions in `*.tf.py` files. Blocks must be yielded to be included in the generated JSON files.

Blocks are the most fundamental part of Terraform configuration. Read the [documentation](https://www.terraform.io/docs/configuration/syntax.html) to learn more about blocks.

Signature:

```python
def block(block_type: str, *labels: str, body: Optional[dict] = None) -> Block

block_type:
    block type such as "resource", "variable", "provider"
labels:
    labels for the block
body:
    the body of the block

returns:
    configuration block
```

Example:

```python
from pretf.api import block


def pretf_blocks():

    # The group resource is defined in another file,
    # but we want to reference it here, so we can
    # create a block with an empty body. It is not
    # yielded so it won't be included in the JSON.
    group = block("resource", "aws_iam_group", "example", {})

    # Create and yield a block to include it in the JSON.
    user = yield block("resource", "aws_iam_user", "example", {
        "name": "example",
    })

    # Create and yield another block, this time demonstrating
    # how block attributes can be accessed. The resulting JSON
    # will contain Terraform references like:
    #   "users": "${aws_iam_user.example.name}",
    #   "groups": ["${aws_iam_group.example.name}"]
    yield block("resource", "aws_iam_user_group_membership", "example", {
        "user": user.name,
        "groups": [group.name]
    })
```

## log

<h3>log.accept</h3>

Prompts the user to enter "yes" or "no". Returns `True` if the response was "yes", otherwise `False`. Pressing Ctrl-C counts as "no".

Signature:

```python
def accept(message: Any) -> bool:

message:
    the message to display

returns:
    whether the user entered "yes"
```

Example:

```python
from pretf.api import log


def pretf_workflow():
    if log.accept("do you wish to continue?"):
        print("user accepted the prompt")
    else:
        print("user did not accept the prompt")
```

<h3>log.bad</h3>

Displays a message prefixed with `[pref]` in red.

Signature:

```python
def bad(message: Any) -> None:

message:
    the message to display

returns:
    None
```

Example:

```python
from pretf.api import log


def pretf_workflow():
    log.bad("something bad happened")
```

<h3>log.ok</h3>

Displays a message prefixed with `[pref]` in cyan.

Signature:

```python
def ok(message: Any) -> None:

message:
    the message to display

returns:
    None
```

Example:

```python
from pretf.api import log


def pretf_workflow():
    log.bad("something normal happened")
```
