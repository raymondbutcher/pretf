# Example: flattened directory layout

When compared to the `workspaces` layout, the `flatten` layout:

Pros:

* has more obvious environment directories
    * `cd` and `ls` the directories to see what exists
* is easier to switch between environments
    * `cd` into `iam/dev` to work with the `iam` stack in the `dev` environment 
* has more options for S3 backend separation
    * each environment could use a separate backend
    * all environments within an account could share a backend
    * all environments in all accounts could share a backend
Cons:

* has more symlinks
    * one for each file in the parent directories
