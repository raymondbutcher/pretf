When Pretf runs, it looks for a `pretf.py` file in the current directory or parent directories. If found, Pretf will call the `pretf_workflow()` function from that file.

The following `pretf.py` file implements the default behaviour of Pretf. This is only useful as an example to use for getting started with your own custom workflow.

```python
# pretf.py

from pretf import workflow


def pretf_workflow():
    # Delete *.tf.json and *.tfvars.json files.
    delete_files()

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    create_files()

    # Execute Terraform.
    return execute_terraform()
```

The `pretf_workflow()` function is called with no arguments, and it should return an exit code (e.g. 0 for success, 1 for error). The above example returns the exit code returned by Terraform, which is the recommended approach.

To customise the behaviour of Pretf, create this file and customise as required.
