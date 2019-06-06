# Pretf

**Note: This is in early development. Things are not yet implemented. The API may change.**

Pretf is a completely transparent, drop-in Terraform wrapper that generates Terraform configuration with Python. It requires no configuration and no changes to standard Terraform projects to start using it.

Terraform includes first-class support for configuration in JSON files. Pretf generates those JSON files using your Python functions.

## Documentation

The documentation for Pretf is located at: [https://pretf.readthedocs.io/](https://pretf.readthedocs.io/)

## Features and goals

* Drop into any standard Terraform project.
    * Configuration is optional and often unnecessary.
    * Just add Python files next to the Terraform files.
    * Standard Terraform command line usage.
* Obvious.
    * Projects using Pretf are like standard Terraform projects but with extra Python files.
    * Python files in projects are self-explanatory; their purpose is obvious.
* Minimal.
    * No concept of specific Terraform resources, instead there is a generic way to output JSON configuration blocks.
    * Small API.
    * Small project scope.
    * Easy to learn.
* Flexible.
    * Change the entire workflow if you want.
