# Custom workflows

When Pretf runs, it looks for a `pretf.py` file in the current directory. If found, Pretf will all the `run()` function from that file.

The following `pretf.py` file performs the default behaviour of Pretf:

```python
# pretf.py

import sys

from pretf.core import execute, tf


def run():
    # Create *.tf.json files from *.tf.py files.
    tf.create()

    # Execute Terraform.
    return execute("terraform")
```

The `run()` function is called with no arguments, and it should return an exit code (e.g. 0 for success, 1 for error). The above example returns the exit code from Terraform, which is the recommended approach.

To customise the behaviour of Pretf, create a similar file and customise as required.

## Cleaning up files

When creating `*.tf.json` files from `*.tf.py` files, it is easy to create "orphan" files that are no longer irrelvant.

For example, if `users.tf.py` is used to create `users.tf.json` and then `users.tf.py` gets deleted, the generated `users.tf.json` may still exist unless it is dealt with.

The following `pretf.py` file shows how to clean up old `*.tf.json` files:

```python
# pretf.py

import sys

from pretf.core import execute, tf


def run():
    # Create *.tf.json files from *.tf.py files.
    created = tf.create()

    # Remove all *.tf.json files except for the ones created just now.
    tf.remove(exclude=created)

    # Execute Terraform.
    return execute("terraform")
```
