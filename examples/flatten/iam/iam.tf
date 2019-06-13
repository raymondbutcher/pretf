resource "aws_iam_user" "pretf" {
  name = "pretf-workspaces-flatten-${var.stack}"
}

# Example of including a local module.
# Note that the source path is relative to the stack-environment
# directory and not this file. This file gets symlinked into the
# other directory, Terraform runs there and uses the symlink.

module "disable_user" {
  source    = "../../modules/iam-disable-user"
  user_name = aws_iam_user.pretf.name
}
