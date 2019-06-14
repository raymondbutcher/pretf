# Example: workspaces layout

When compared to the `flatten` layout, the `workspaces` layout:

Pros:

* has fewer symlinks
    * one to set up the backend
    * one to define variables
        * this could potentially be avoided with other tricks

Cons:

* has less obvious environments
    * run `terraform workspace show` or set up a custom shell prompt to display the current environment
* is harder to switch between environments
    * run `terraform workspace list` and `terraform workspace select <name>`
* cannot have separate S3 backend resources across different accounts
    * because `terraform workspace list` inspects the bucket for the available workspaces
    * all workspaces in a stack must share the same backend
    * "dev" and "prod" environment state would be stored in the same S3 bucket, preferable in a management account
