# Example: Jinja2 templates

This shows how to use Jinja2 templates to create Terraform resources and variables.

Pretf renders `*.tf.j2` and `*.tfvars.j2` into `*.tf` and `*.tfvars` in-memory, but then parses them and writes them as JSON files. The extra step of converting them to JSON files makes it easier to clean up generated files and makes for simpler `.gitignore` rules.
