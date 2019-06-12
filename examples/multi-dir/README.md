# Example: Multi-dir project

This shows multiple `stack` directories each containing `environment` directories.

## src

This directory contains shared files used by the whole project. Specifically it contains `stack.tf.py` which generates the Terraform S3 backend and AWS provider blocks. This file is used by both `iam` and `vpc` stacks.

An alternate approach would be to keep a copy of `stack.tf.py` in each stack environment directory.

## iam/src

This directory contains the infrastructure code for the `iam` stack. This is where resources like `aws_iam_user` are defined.

## iam/dev

This directory contains only 2 files. `iam.dev.auto.tfvars` sets the Terraform variable values for this environment. `pretf.py` specifies the custom workflow which symlinks files from the 2 aforementioned `src` directories into the current directory before generating `tf.json` files and executing Terraform.

## iam/prod

This directory is the same as `iam/dev` but with different variable values.

## vpc

This follows the same structure as the `iam` directory.
