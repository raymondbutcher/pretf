# Example: Security groups

This shows how to create dynamic security group rules. Given a single list of CIDR blocks, it checks whether they are public or private, and adds a rule to the relevant security group. It also adds each CIDR as a separate rule resource, which allows Terraform to manage the resources individually.

It also shows how Pretf can be dropped into a project to generate a single file without requiring any other configuration or project changes. 

Only `sg.tf.py` is non-standard for a Terraform project. When `pretf` runs it generates `sg.tf.json` and then executes `terraform`.
