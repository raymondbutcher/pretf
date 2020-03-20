resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr_block

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "pretf-workspaces-flatten-${var.environment}"
    Environment = var.environment
  }
}
