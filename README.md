# Pretf

Pretf is a Python library for generating Terraform configuration and optionally executing Terraform afterwards. This is Infrastructure as Code, not Infrastructure as Configuration Language!

Terraform is good at managing resources, and the configuration language HCL is quite easy to read, but it is easy to run into limitations of that language. Luckily, Terraform also supports configuration as JSON files. Pretf allows you to write Python code, with for-loops and everything, and output simple JSON files for Terraform to use.

## Project status

This is in very early development. Things are not yet implemented. The API is likely to change as I experiment with different use-cases and try things out.
