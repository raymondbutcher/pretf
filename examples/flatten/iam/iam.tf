resource "aws_iam_user" "pretf" {
  name = "pretf-workspaces-flatten-${var.stack}"
}
