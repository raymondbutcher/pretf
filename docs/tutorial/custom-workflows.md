When Pretf runs, it looks for a `pretf.py` file in the current directory. If found, Pretf will call the `run()` function from that file.

The following `pretf.py` file implements the default behaviour of Pretf. This is only useful as an example to use for getting started with your own custom workflow.

```python
# pretf.py

from pretf.core import execute, tf


def run():
    # Create *.tf.json files from *.tf.py files.
    tf.create()

    # Execute Terraform.
    return execute("terraform")
```

The `run()` function is called with no arguments, and it should return an exit code (e.g. 0 for success, 1 for error). The above example returns the exit code from Terraform, which is recommended approach.

To customise the behaviour of Pretf, create this file and customise as required.

## Clean up files

When creating `*.tf.json` files from `*.tf.py` files, it is possible to have files that are no longer relevant.

For example, if `users.tf.py` creates `users.tf.json` and then `users.tf.py` gets deleted, the generated `users.tf.json` may still exist. This leftover file is a problem as it may define resources that should no longer exist. This is more likely to occur when working in teams; the person that deleted `users.tf.py` may have deleted their copy of `users.tf.json` but the other team members may be unaware of the change.

The following `pretf.py` file shows how to automatically clean up old `*.tf.json` files:

```python
# pretf.py

from pretf.core import execute, tf


def run():
    # Create *.tf.json files from *.tf.py files.
    created = tf.create()

    # Remove all *.tf.json files except for the ones created just now.
    # This assumes that there are no manually created *.tf.json files.
    tf.remove(exclude=created)

    # Execute Terraform.
    return execute("terraform")
```
