# Parameters

Let's start by showing `pretf.py` and `random.tf.py` from the previous pages, plus a new file `users.tf.py`. We can see that `random.tf.py` and `users.tf.py` are mixing data and resources, which is not always ideal.

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

```python
# random.tf.py

from pretf.core import tf


def terraform():
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]
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
    users = ["ray", "violet"]
    for name in users:
        yield tf(f"resource.aws_iam_user.{name}", {"name": name})
```

### Using parameters

Let's pass parameters in from `pretf.py` rather than defining data and resources in the same files. To use parameters, pass them into the `tf.create()` function as keyword arguments and handle them in every `terraform()` function:

```python
# pretf.py

import sys

from pretf.core import execute, tf


def run():
    # Create *.tf.json files from *.tf.py files,
    # passing in parameters to the terraform() functions.
    created = tf.create(
        animals=["dog", "cat", "buffalo", "rabbit", "badger"],
        users=["ray", "violet"],
    )

    # Remove all *.tf.json files except for the ones created just now.
    tf.remove(exclude=created)

    # Execute Terraform.
    return execute("terraform")
```

```python
# random.tf.py

from pretf.core import tf


def terraform(animals, users):
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


def terraform(animals, users):
    for name in users:
        yield tf(f"resource.aws_iam_user.{name}", {"name": name})
```

### Using '**kwargs' for tidy functions

The function in `random.tf.py` needs the `animals` parameter, but not the `users` paramater. Conversely, the function in `users.tf.py` needs the `users` parameter but not the `animals` parameter.

To improve these functions, we can use `**kwargs` in the function signatures to collect all irrelevant parameters and then do nothing with them.

This pattern becomes much more useful as the number of unused parameters increases.

```python
# random.tf.py

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
