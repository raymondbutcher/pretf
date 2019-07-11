data "aws_caller_identity" "dev" {
  provider = aws.dev
}

data "aws_caller_identity" "prod" {
  provider = aws.prod
}

data "aws_vpc" "dev" {
  provider = aws.dev
  tags = {
    Environment = "dev"
  }
}

data "aws_vpc" "prod" {
  provider = aws.prod
  tags = {
    Environment = "prod"
  }
}

resource "aws_vpc_peering_connection" "prod_to_dev" {
  provider      = aws.prod
  vpc_id        = data.aws_vpc.prod.id
  peer_owner_id = data.aws_caller_identity.dev.account_id
  peer_vpc_id   = data.aws_vpc.dev.id
}

resource "aws_vpc_peering_connection_accepter" "prod_to_dev" {
  provider                  = aws.dev
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dev.id
  auto_accept               = true
}
