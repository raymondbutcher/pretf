# Example: testing with pytest

This shows a test that creates Terraform configuration, runs Terraform, and then make assertions about its output. Pytest is not automatically installed when you install Pretf. Install it with `pip install pytest` or add `pytest` to the `requirements.txt` of your project.

## Usage

Run the following command:

```shell
pytest
```

Or for more verbose output:

```
pytest -v
```
