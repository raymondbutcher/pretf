# Example: versioned root modules

This is an example project that uses Terraform configuration from a separate git repository. Only the `.tfvars` file exists in each environment directory.

Features:

* Environments use versioned configuration
    * You can have dev and production each pointing to different version tags. This avoids situations like when you have applied a change to dev, are now testing it, but are not ready to apply it to production. In that situation you would avoid running Terraform against production because the changes haven't been fully tested in dev yet. The code doesn't match the desired state of the infrastructure.
* Directory-based
    * Change into an environment directory and run Terraform
    * No extra CLI arguments required when running Terraform
* Simple directory layout allowing for DRY code
* One persistent `.terraform directory` per environment
    * No need to run `terraform init` more than once per environment

## Working locally

To test local changes in the root module, you can temporarily update the `.tfvars` file to point to a local path. The `pretf.workflow.py` has been written to use the first matching line, so you can swap the lines around to switch between the local and remote value.

> Note: Terraform does not support module paths starting with `~/` so use the full path to your home directory if required.

> Note: Don't accidentally commit it!

> Note: You are not limited to defining the root module source in this way; this is just how it has been implemented in this example. Suggestions are welcome!

```tf
# pretf: source = "/home/ray/github/pretf-example-modules/pass/"
# pretf: source = "github.com/raymondbutcher/pretf-example-modules//pass?ref=v1.1.0"
```
