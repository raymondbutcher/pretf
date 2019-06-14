Pretf provides a way to generate Terraform configuration with Python code. It should be seen as an extension for Terraform projects, to be used in situations where the standard configuration language is not working well for your project.

* If you are not familiar with Terraform:
    * Start with Terraform, not Pretf
* If you are familiar with Terraform:
    * If it works well for your project:
        * Continue using Terraform without Pretf
    * If you're using "workarounds", "escape hatches", or "hacks":
        * Consider using Pretf

These tutorials assume you have an existing Terraform project and you want to generate additional resources with Pretf.

Before starting, run `pretf version` to check that Pretf and Terraform are installed:

```shell
$ pretf version
Pretf v0.3.0
Terraform v0.12.1
+ provider.aws v2.12.0
+ provider.random v2.1.2
```
