## Starting code

Let's start by showing `pretf.py` and `animals.tf.py` from the previous pages, plus a new file `users.tf.py`. We can see that `animals.tf.py` and `users.tf.py` are hardcoding their data: the lists of animals and users.

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

```python
# animals.tf.py

from pretf.core import tf


def terraform():
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]  # hardcoded
    for name in animals:
        animal = yield tf(f"resource.random_integer.{name}", {
            "min": 1,
            "max": 10,
        })
        yield tf(f"output.{name}", {
            "vaue": animal.result,
        })
```

```python
# users.tf.py

from pretf.core import tf


def terraform():
    users = ["ray", "violet"]  # hardcoded
    for name in users:
        yield tf(f"resource.aws_iam_user.{name}", {"name": name})
```

## Basic parameter usage

Let's pass parameters in from `pretf.py`. To use parameters, pass them into the `tf.create()` function as keyword arguments and handle them in every `terraform()` function:

```python
# pretf.py

from pretf.core import execute, tf


def run():
    # Create *.tf.json files from *.tf.py files,
    # passing parameters into the terraform() functions.
    created = tf.create(
        animals=["dog", "cat", "buffalo", "rabbit", "badger"],
        users=["ray", "violet"],
    )

    # Remove all *.tf.json files except for the ones created just now.
    # This assumes that there are no manually created *.tf.json files.
    tf.remove(exclude=created)

    # Execute Terraform.
    return execute("terraform")
```

```python
# animals.tf.py

from pretf.core import tf


def terraform(animals, users):  # parameters from pretf.py
    for name in animals:
        animal = yield tf(f"resource.random_integer.{name}", {
            "min": 1,
            "max": 10,
        })
        yield tf(f"output.{name}", {
            "vaue": animal.result,
        })
```

```python
# users.tf.py

from pretf.core import tf


def terraform(animals, users):  # parameters from pretf.py
    for name in users:
        yield tf(f"resource.aws_iam_user.{name}", {"name": name})
```

## Using '**kwargs' in function signatures

The function in `animals.tf.py` needs the `animals` parameter, but not the `users` paramater. Conversely, the function in `users.tf.py` needs the `users` parameter but not the `animals` parameter.

To improve these functions, we can use `**kwargs` in the function signatures to collect all irrelevant parameters and then do nothing with them.

This pattern becomes much more useful as the number of unused parameters increases.

```python
# animals.tf.py

from pretf.core import tf


def terraform(animals, **kwargs):
    for name in animals:
        animal = yield tf(f"resource.random_integer.{name}", {
            "min": 1,
            "max": 10,
        })
        yield tf(f"output.{name}", {
            "vaue": animal.result,
        })
```

```python
# users.tf.py

from pretf.core import tf


def terraform(users, **kwargs):
    for name in users:
        yield tf(f"resource.aws_iam_user.{name}", {"name": name})
```

## Why not Terraform variables?

Pretf is a little side project which is intentionally small and simple. To support Terraform variables correctly, the following would be required:

* Support `TF_VAR_*` environment variables
* Support `-var` command line arguments
* Support `-var-file` command line arguments
* Parse `*.tf` files for variables and their default values
* Parse `*.tfvars` files for values
* Parse `*.tf.json` files for variables and their default values
* Parse `*.tfvars.json` files for values
* Process `*.tf.py` files concurrently, parsing their output for variables, blocking variable access until the variable is defined and populated, handling deadlocks and missing variables

That is a non-trivial amount of work, and not worth it unless this project becomes popular.
