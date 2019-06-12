resource "aws_iam_user" "pretf" {
  name = "pretf-workspaces-multi-dir-${var.stack}"
}
