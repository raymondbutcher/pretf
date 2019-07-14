# Example: flattened directory layout

This is an example project that "flattens" stack directories using symlinks. This is a simple and obvious project structure that is easy to work with.

Features:

* Directory-based
    * Change into an environment directory and run Terraform
    * No extra CLI arguments required when running Terraform
* Simple directory layout allowing for DRY code
* One persistent `.terraform directory` per environment
    * No need to run `terraform init` more than once
* Automatic AWS credentials when running locally
    * With MFA token support
* Ability to use Python for anything that is too complicated or not supported in HCL

## Comparison to workspaces layout

When compared to the `workspaces` layout, the `flatten` layout:

Pros:

* Has more obvious environment directories
    * `cd` and `ls` the directories to see what exists
* Is easier to switch between environments
    * `cd` into `iam/dev` to work with the `iam` stack in the `dev` environment 
* Has more options for S3 backend separation
    * Each environment could use a separate backend
    * All environments within an account could share a backend
    * All environments in all accounts could share a backend

Cons:

* Has more symlinks
    * One for each file in the parent directories
