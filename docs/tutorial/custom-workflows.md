When Pretf runs, it looks for a `pretf.py` file in the current directory. If found, Pretf will call the `run()` function from that file.

The following `pretf.py` file implements the default behaviour of Pretf. This is only useful as an example to use for getting started with your own custom workflow.

```python
# pretf.py

from pretf.run import create, execute, remove


def run():
    # Delete *.tf.json files.
    remove()

    # Create *.tf.json files from *.tf.py files.
    create()

    # Execute Terraform.
    return execute()
```

The `run()` function is called with no arguments, and it should return an exit code (e.g. 0 for success, 1 for error). The above example returns the exit code returned by Terraform, which is recommended approach.

To customise the behaviour of Pretf, create this file and customise as required.
