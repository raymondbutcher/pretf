The previous page has 5 dynamic resources but nothing is done with them. To access an attribute of a resource, just... access it.

This does not return the actual dynamic value of the resource managed by Terraform. Instead, it returns an interpolation reference string for Terraform to use when it runs.

```python
# animals.tf.py

from pretf.api import block


def pretf_blocks(var):
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]
    for name in animals:
        animal = yield block("resource", "random_integer", name, {
            "min": 1,
            "max": 10,
        })
        yield block("output", name, {
            "value": animal.result,  # access "result" attribute of resource
        })
```

Now run `pretf validate` and the resulting JSON file will contain the additional outputs. Inspecting the generated JSON file shows that `animal.result` was translated into `"${resource.random_integer.dog.result}"` for the `dog` iteration of the loop.

Accessing any attribute of a block object will return a string containing a Terraform reference to that attribute. This lets you take advantage of Terraform's [implicit resource dependencies](https://learn.hashicorp.com/terraform/getting-started/dependencies.html).

## Assign and yield

The above code contains the pattern `result = yield block(...)`.

Pretf sends yielded values back to generators. This allows functions assign block objects to a variable and yield them in the same line.

## Reference without yielding

If something is defined in another file, but you still want to reference it, then create a block object with no body. Do not `yield` it, because that would include it in the `*.tf.json` output.

```python
yield block("output", name, {
    "value": block("resource", "random_integer", name).result,
})
```
