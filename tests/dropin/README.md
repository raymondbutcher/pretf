# Example: drop in

This shows how Pretf can be dropped into a project to generate a single file without requiring any other configuration or project changes. 

Only `iam.tf.py` is non-standard for a Terraform project. When `pretf` runs it generates `iam.tf.json` and then executes `terraform`.
