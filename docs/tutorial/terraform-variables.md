## Starting code

Let's start by showing `animals.tf.py` from the previous pages, plus a new file `users.tf.py`. We can see that these files are hardcoding their data: the lists of animals and users.

```python
# animals.tf.py

from pretf.api import block


def pretf_blocks():
    animals = ["dog", "cat", "buffalo", "rabbit", "badger"]  # hardcoded
    for name in animals:
        animal = yield block("resource", "random_integer", name, {
            "min": 1,
            "max": 10,
        })
        yield block("output", name, {"value": animal.result})
```

```python
# users.tf.py

from pretf.api import tf


def pretf_blocks():
    users = ["ray", "violet"]  # hardcoded
    for name in users:
        yield block("resource", "aws_iam_user", "name", {
            "name": name,
        })
```

## Terraform variables

Terraform variables can be accessed in Pretf by adding a `var` argument to the `pretf_blocks()` function. Pretf will see this argument in the function signature and pass in a variables object. Let's use that instead of hardcoding values:


```terraform
# variables.tf

variable "animals" {
  type = list(string)
}

variable "users" {
  type = list(string)
}
```

```terraform
# terraform.tfvars

animals = ["dog", "cat", "buffalo", "rabbit", "badger"]

users = ["ray", "violet"]
```

```python
# animals.tf.py

from pretf.api import block


def pretf_blocks(var): # var added to the function signature
    for name in var.animals: # accessing a variable
        animal = yield block("resource", "random_integer", name, {
            "min": 1,
            "max": 10,
        })
        yield block("output", name, {
            "value": animal.result,
        })
```

```python
# users.tf.py

from pretf.api import block


def pretf_blocks(var): # var added to the function signature
    for name in var.users: # accessing a variable
        yield block("resource", "aws_iam_user", name, {
            "name": name
        })
```

# Variable definition precedence

From the [Terraform documentation](https://www.terraform.io/docs/configuration/variables.html#variable-definition-precedence
):

<blockquote>
    <p>Terraform loads variables in the following order, with later sources taking precedence over earlier ones:</p>
    <ul>
        <li>Environment variables.</li>
        <li>The <code>terraform.tfvars</code> file, if present.</li>
        <li>The <code>terraform.tfvars.json</code> file, if present.</li>
        <li>Any <code>*.auto.tfvars</code> or <code>*.auto.tfvars.json</code> files, processed in lexical order of their filenames.</li>
        <li> Any <code>-var</code> and <code>-var-file</code> options on the command line, in the order they are provided.</li>
    </ul>
</blockquote>

Pretf uses the same rules when resolving variable values.

If a project has `*.tfvars.py` files to generate `*.tfvars.json` files that would change the value of a variable (i.e. one of the above sources has already set the variable to a different value) then Pretf will exit with a descriptive error message. This ensures that Python and Terraform run with consistent variable values.
