resource "aws_iam_user" "pretf" {
  name = "pretf-workspaces-${terraform.workspace}"
}
