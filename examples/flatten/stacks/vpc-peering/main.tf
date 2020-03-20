data "aws_caller_identity" "dev" {
  provider = aws.dev
}

resource "aws_vpc_peering_connection" "prod_to_dev" {
  provider      = aws.prod
  vpc_id        = var.prod_vpc_id
  peer_owner_id = data.aws_caller_identity.dev.account_id
  peer_vpc_id   = var.dev_vpc_id
}

resource "aws_vpc_peering_connection_accepter" "prod_to_dev" {
  provider                  = aws.dev
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dev.id
  auto_accept               = true
}

# Options can't be set until the connection has been accepted and is active,
# so create an explicit dependency on the accepter when setting options.

locals {
  active_vpc_peering_connection_id = aws_vpc_peering_connection_accepter.prod_to_dev.id
}

resource "aws_vpc_peering_connection_options" "prod" {
  provider                  = aws.prod
  vpc_peering_connection_id = local.active_vpc_peering_connection_id
  requester {
    allow_remote_vpc_dns_resolution = true
  }
}

resource "aws_vpc_peering_connection_options" "dev" {
  provider                  = aws.dev
  vpc_peering_connection_id = local.active_vpc_peering_connection_id
  accepter {
    allow_remote_vpc_dns_resolution = true
  }
}
