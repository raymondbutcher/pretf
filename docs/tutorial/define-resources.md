The primary feature of Pretf is to read `*.tf.py` files and create matching `*.tf.json` files. These JSON files are supported by Terraform as an alternative to the more commonly used `*.tf` files.

Start by creating a file named `animals.tf.py` in your Terraform project directory:

```python
# animals.tf.py

from pretf.api import block


def pretf_blocks(var):
    yield block("resource", "random_integer", "dog", {
        "min": 1,
        "max": 10,
    })

    yield block("resource", "random_integer", "cat", {
        "min": 1,
        "max": 10,
    })

    yield block("resource", "random_integer", "buffalo", {
        "min": 1,
        "max": 10,
    })
```

The function must be named `pretf_blocks()` for Pretf to find it.

Now run `pretf validate`, which will generate a JSON file and run `terraform validate`:

```shell
$ pretf validate
[pretf] create: animals.tf.json
[pretf] run: terraform validate
Success! The configuration is valid.
```

If you saw:

```shell
Error: provider.random: no suitable version installed
  version requirements: "(any version)"
  versions installed: none
```

Then you probably need to run `pretf init` to install the Random provider. This is standard Terraform behaviour and nothing to do with Pretf, except that Pretf runs Terraform . Run `pretf init` and then `pretf validate` again.

With Terraform successfully validating your generated JSON file, you can now run `pretf plan` or `pretf apply` to manage the new resources. You can still run `terraform` directly, but using `pretf` as a wrapper will ensure that generated JSON files are always up to date.

## The 'yield' keyword

If you are not familiar with the `yield` keyword in the above code, then read about [Python Generators](https://www.python.org/dev/peps/pep-0255/) introduced in Python 2.2. Normally we might create a list, append elements to that list, and then return the list at the end of the function. Instead, we can just `yield` each element as we go.

## Translate HCL to Python

Translating HCL code into Python block objects is very simple. They are constructed in the same way as the original HCL, only requiring slight adjustments to be valid Python syntax.

The following HCL resource:

```terraform
resource "random_integer" "dog" {
  min = 1
  max = 10
}
```

Consists of a block type, labels, and the body. Simply take each part of the above and convert them into valid Python types (str and dict) ensure they are quoted appropriately.

Then just pass them into the `block()` function:

```python
block("resource", "random_integer", "dog", {
    "min": 1,
    "max": 10,
})
```
