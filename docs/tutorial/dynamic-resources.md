# Dynamic resources

In the previous tutorial, `random.tf.py` defined 3 resources:

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

There is a lot of duplication here, and what if we want to add more animals? Let's use a for-loop:

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

Now run `pretf validate` and the resulting JSON file will contain those 5 resources.

## The 'f-string' literal

If you are not familiar with the syntax of `f"resource.random_integer.{animal}"` in the above code, then read about [Python f-strings](https://www.python.org/dev/peps/pep-0498/) introduced in Python 3.6. Normally you might write it as `"resource.random_integer.{}".format(animal)` but f-strings allow for similar string formatting features with less code.

## Why not use 'count'?

Terraform supports creating resources from a list like this:

```terraform
resource "random_integer" "animals" {
  count = length(var.animals)
  min = 1
  max = 10
}
```

But at the time of this writing, Terraform 0.12.0 is the latest version, and it still [recreates resources when you change the list](https://github.com/hashicorp/terraform/issues/17179).
