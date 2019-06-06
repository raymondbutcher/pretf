# Example: IAM users

This shows how to create dynamic IAM users from a variable, using dynamic resource names to avoid the pitfalls of standard `count` in Terraform.

It also shows how Pretf can be dropped into a project to generate a single file without requiring any other configuration or project changes. 

Only `iam.tf.py` is non-standard for a Terraform project. When `pretf` runs it generates `iam.tf.json` and then executes `terraform`.
