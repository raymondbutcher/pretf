# Define resources

The primary feature of Pretf is to read `*.tf.py` files and create matching `*.tf.json` files. These JSON files are supported by Terraform as an alternative to the more commonly used `*.tf` files.

Start by creating a file named `random.tf.py` in your Terraform project directory:

```python
from pretf.core import tf


def terraform():
    yield tf("resource.random_integer.dog", {
        "min": 1,
        "max": 10,
    })

    yield tf("resource.random_integer.cat", {
        "min": 1,
        "max": 10,
    })

    yield tf("resource.random_integer.buffalo", {
        "min": 1,
        "max": 10,
    })
```

Note that the function must be named `terraform` for Pretf to find it.

Now run `pretf validate`, which will generate a JSON file and run `terraform validate`:

```shell
$ pretf validate
[pretf] create: random.tf.json
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

## Translating HCL to Python

HCL resource:

```terraform
resource "random_integer" "dog" {
  min = 1
  max = 10
}
```

Python resource:

```python
tf("resource.random_integer.dog", {
    "min": 1,
    "max": 10,
})
```

The signature for the `tf` object is `tf(name: str, data: dict)`.

HCL name:

```terraform
resource "random_integer" "dogs"
```

Python name:

```python
"resource.random_integer.dogs"
```

HCL data:

```terraform
{
  min = 1
  max = 10
}
```

Python data:

```
{
  "min": 1,
  "max": 10,
}
```
