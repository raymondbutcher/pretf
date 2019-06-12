There is too much duplication on the previous page, and what if we want to add more animals? Let's use a 'for loop':

```python
# animals.tf.py

from pretf.api import block


def terraform(var):
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]
    for name in animals:  # loop over list
        yield block("resource", "random_integer", name, {  # dynamic resource name
            "min": 1,
            "max": 10,
        })
```

Now run `pretf validate` and the resulting JSON file will contain those 5 resources.

## The 'for' statement

Unlike Terraform, Python (and by extension Pretf) supports 'for loops'. Normally, we might write the same Terraform code multiple times, with slight differences in the resource name and/or arguments. With Pretf, we can use a 'for loop'.

## Why not use 'count'?

Terraform supports creating resources from a list like this:

```terraform
resource "random_integer" "animals" {
  count = length(var.animals)
  min   = 1
  max   = 10
}
```

But at the time of this writing, Terraform 0.12.0 is the latest version, and it still [recreates resources when you change the list](https://github.com/hashicorp/terraform/issues/17179).
