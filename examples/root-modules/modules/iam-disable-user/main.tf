variable "user_name" {}

data "aws_iam_policy_document" "deny_all" {
  statement {
      effect = "Deny"

    actions = [
      "*",
    ]

    resources = [
      "*",
    ]
  }
}

resource "aws_iam_user_policy" "disabled" {
  name = "${var.user_name}-disabled"
  user = var.user_name
  policy = data.aws_iam_policy_document.deny_all.json
}
