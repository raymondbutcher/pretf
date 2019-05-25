# Example: custom

This shows a more complete Pretf project, including the following:

* Define configuration for different environments (`dev` and `prod`) and use code from another directory (`src`)
    * Reuse the same code in multiple environments
* Clean up orphan `*.tf.json` files
    * If a `*.tf.py` file is deleted then Pretf will automatically delete the previously created `*.tf.json` file before executing Terraform
