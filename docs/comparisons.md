Note that these comparisons are mostly based on impressions of these projects, not necessarily based on experience from using them.

## Terraform

Pretf is not a replacement for Terraform. It is used to generate Terraform configuration files, and then run Terraform. Pretf can be used to generate more complicated Terraform configuration files than the Terraform configuration language normally allows.

## Terragrunt

On the surface, Terragrunt appears to:

1. Add extra functions to Terraform (with interpolation syntax, in a place where Terraform will ignore it).
2. Work with some Terragrunt-specific conventions or patterns to provide extra features on top of Terraform.

Pretf avoids working within the confines of `*.tf` files or supplied functions, instead letting you write Python code, and write your own functions. This is much more flexible, as long as you are familiar with Python.

Pretf has fewer conventions and should be easier for newcomers to understand. The extra `*.tf.py` files in projects using Pretf should be fairly self-explanatory to anyone that can read Python code.

The most complicated part of Pretf projects will be when a `pretf.py` file is added to customise the workflow. However, this file contains the logic of the customised workflow, so it should again be fairly self-explanatory.

Pretf is more flexible and more obvious than Terragrunt, as long as you are familiar with Python.

## Pulumi

Pulumi is an alternative to Terraform that allows you to create resources with Python code, and other languages.

The Pulumi SDK includes classes for every resource, while Pretf only uses generic strings and dictionaries. Pulumi's approach allows for IDE features like autocompletion and error checking, but it requires ongoining maintenance and updates to their SDK to support new resources.

If you want to use Terraform, then Pretf gets you some of the selling points of Pulumi (write the logic in Python) wthout making you switch products.

## Custom wrappers

Wrappers written in Bash or Make seem to have some or all of these problems:

1. Have unclear or unobvious command line arguments.
    * Which environment and which account? How many possibile places can this code be deployed to? Do I need to read the documentation or source code to figure this out?
    * The user can make a mistake.
2. Restricted subset of Terraform CLI commands, making it hard to run unsupported commands.
    * E.g. `terraform state mv` not supported, so the user has to figure out how to run that command without losing things that the wrapper was doing such as configuring the backend and passing parameters.
    * The user can make a mistake.
3. Use the same directory for multiple remote backends, so it runs the slow `terraform init` command every time.
4. Require setting AWS credentials before running.
    * Often requires running a separate command, and knowing which credentials to use.
    * The user can make a mistake.

Pretf is a transparent wrapper, meaning it performs its functionality and then executes Terraform, passing along any command line arguments. Transparent wrappers avoid issues 1 and 2.

Pretf can be used to dynamically generate the backend configuration, and work with files from other directories. This allows for directory-based environments or stacks, which avoids issue 3.

Pretf also has good support for AWS credentials and backends. AWS credentials can be set within Python, programattically, so the user does not have to set credentials separately. This avoids issue 4.
