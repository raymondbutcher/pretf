There is too much duplication on the previous page, and what if we want to add more animals? Let's use a 'for loop':

```python
# animals.tf.py

from pretf.api import block


def pretf_blocks():
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]
    for name in animals:  # loop over list
        yield block("resource", "random_integer", name, {  # dynamic resource name
            "min": 1,
            "max": 10,
        })
```

Now run `pretf plan` and you will see those 5 resources.

## Why not use 'count'?

Terraform supports creating resources from a list like this:

```terraform
resource "random_integer" "animals" {
  count = length(var.animals)
  min   = 1
  max   = 10
}
```

But at the time of this writing, Terraform 0.12.4 is the latest version, and it still [recreates resources when you change the list](https://github.com/hashicorp/terraform/issues/17179).
