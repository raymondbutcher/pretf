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
