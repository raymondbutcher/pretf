resource "aws_iam_user" "pretf" {
  name = "pretf-flatten-${var.environment}"
}

# Example of including a local module.
# Note that it is using the "modules" symlink
# created by the pretf.workflow.py file.

module "disable_user" {
  source    = "./modules/iam-disable-user"
  user_name = aws_iam_user.pretf.name
}
