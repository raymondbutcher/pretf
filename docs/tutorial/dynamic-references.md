The previous page has 5 dynamic resources but nothing is done with them. To access an attribute of a resource, just... access it:

```python
# animals.tf.py

from pretf.api import tf


def terraform(var):
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]
    for name in animals:
        animal = yield tf(f"resource.random_integer.{name}", {
            "min": 1,
            "max": 10,
        })
        yield tf(f"output.{name}", {
            "vaue": animal.result,  # access "result" attribute of resource
        })
```

Now run `pretf validate` and the resulting JSON file will contain the additional outputs. Inspecting the generated JSON file shows that `animal.result` was translated into `"${resource.random_integer.dog.result}"` for the `dog` iteration of the loop.

Accessing any attribute of a `tf()` object will return a string containing a Terraform reference to that attribute. This lets you take advantage of Terraform's [implicit resource dependencies](https://learn.hashicorp.com/terraform/getting-started/dependencies.html).

## Assign and yield

The above code contains the pattern `result = yield tf(name, data)`.

Pretf sends yielded values back to generators. This allows functions assign `tf()` objects to a variable and yield them in the same line.

## Reference without yielding

If something is defined in another file, but you still want to reference it, then create a `tf()` object with no body. Do not `yield` it, because that would include it in the `*.tf.json` output.

```python
yield tf("output.dog", {
    "vaue": tf("resource.random_integer.dog").result,
})
```

```python
yield tf(f"output.{name}", {
    "vaue": tf(f"resource.random_integer.{name}").result,
})
```
