# Example: Project

This shows a more complete Pretf project with a custom workflow.

* `src` directory containing infrastructure code
    * Contains `*.tf.py` files that generate `*.tf.json` files
    * Contains standard `*.tf` files
    * Contains module
* `env` directory containing environment-specific code
    * Contains only `pretf.py` and `pretf_env.py` files to customise behaviour of `pretf` command
    * Defines environment-specific parameters to pass into `*.tf.py` functions
    * Cleans up leftover `*.tf.json` files
    * Mirrors contents of `src` directory into current directory using symlinks
    * Creates `*.tf.json` files from `*.tf.py` files 
    * Executes `terraform`
