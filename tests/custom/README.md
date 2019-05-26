# Example: custom

This shows a more complete Pretf project with a custom workflow.

* `src` directory containing infrastructure code
    * Contains `*.tf.py` files that generate `*.tf.json` files
    * Contains standard `*.tf` files
* `dev`, `stage`, and `prod` environment directories
    * Contains only `pretf.py` to customise behaviour of `pretf` command
        * `*.tf.json` files are also committed, only for testing/viewing purposes
    * Defines environment-specific parameters to pass into `*.tf.py` functions
    * Mirrors contents of `src` directory into current directory using symlinks
    * Creates `*.tf.json` files from `*.tf.py` files 
    * Cleans up orphan `*.tf.json` files
    * Executes `terraform`
