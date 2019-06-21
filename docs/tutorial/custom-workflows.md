When Pretf runs, it looks for a `pretf.workflow.py` file in the current or parent directories. If found, Pretf will call the `pretf_workflow()` function from that file.

The following `pretf.workflow.py` file implements a simplified version of the default Pretf behaviour. This is only useful as an example to use for getting started with your own custom workflow.

```python
# pretf.workflow.py

from pretf import workflow


def pretf_workflow():
    # Delete *.tf.json and *.tfvars.json files.
    workflow.delete_files()

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    created = workflow.create_files()

    # Execute Terraform, raising an exception if it fails.
    proc = workflow.execute_terraform()

    # Clean up created files if successful.
    workflow.clean_files(created)

    return proc
```

To customise the behaviour of Pretf, create this file and customise as required.
