variable "vpc_id" {}

resource "aws_security_group" "this" {
  name        = "pretf-enterprise-${var.environment}"
  description = "Security group for enterprise example"
  vpc_id      = var.vpc_id
}

output "security_group_id" {
  value = aws_security_group.this.id
}
