resource "aws_iam_user" "pretf" {
  name = "pretf-workspaces-${terraform.workspace}"
}

module "disable_user" {
  source    = "../../modules/iam-disable-user"
  user_name = aws_iam_user.pretf.name
}
