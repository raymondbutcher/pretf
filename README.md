# Pretf

**Note: This is in very early development. Things are not yet implemented. The API may change as I experiment with different use-cases and try things out.**

Pretf is a completely transparent, drop-in Terraform wrapper that generates Terraform configuration with Python. It requires no configuration and no changes to standard Terraform projects to start using it.

Terraform is good at managing resources, and the configuration language HCL is sometimes quite nice, but HCL is very limited when compared to Python. Luckily, Terraform also supports configuration as JSON files. Pretf allows you to write Python code, with for-loops and everything, to output simple JSON files for Terraform.

## Documentation

The documentation for Pretf is located at: [https://pretf.readthedocs.io/](https://pretf.readthedocs.io/)

## Features and goals

* Drop into any standard Terraform project.
    * Configuration is optional.
    * No changes are required to standard Terraform projects.
    * Standard Terraform command line usage.
* Super flexible.
    * Change the entire workflow if you want.
* Small codebase.
    * No concept of the hundreds or thousands of Terraform resources, instead there is a generic way to create JSON for them.
* Easy to learn.
    * It should take only a few minutes to fully understand Pretf if you know Python.

## Background

I have spent over 2 years building and supporting infrastructure with Terraform. Terraform regularly forces me write code that is ugly and unintuitive. Some things are impossible without calling external scripts, or using wrappers like [Jinjaform](https://github.com/claranet/jinjaform).

Jinjaform has been successful in some respects. It has made some mostly impossible tasks possible. However, the mixture of Jinja2 templates and HCL is ugly. In an attempt to make those templates cleaner, support for custom Jinja2 filters and functions (written in Python) was added. So now Jinjaform mixes HCL, Jinja2 and Python. Pretf is the next step, just getting out of the way and letting you write some Python code.
