# Dynamic references

In the previous tutorial, `random.tf.py` contained 5 dynamic resources:

```python
from pretf.core import tf


def terraform():
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]
    for name in animals:
        yield tf(f"resource.random_integer.{name}", {
            "min": 1,
            "max": 10,
        })
```

Pretf provides an easy way to reference Terraform objects returned by `tf()`:

```python
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

Now run `pretf validate` and the resulting JSON file will contain the additional outputs.

Inspecting the generated JSON file shows that Pretf translated `animal.result` into `"${resource.random_integer.dog.result}"` for the `dog` iteration of the loop.

## Assigning and yielding

The above code contained the pattern `result = yield tf(name, data)`.

Pretf sends yielded values back to generators. This allows functions to yield `tf()` objects and assign them in the same line.
