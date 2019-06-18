# Data sources are used to find out information about
# the VPCs to be peered. Alternatively, these could be
# fetched from a remote state data source, or the peering
# could be done in the same stack as the VPC creation.

data "aws_caller_identity" "nonprod" {
  provider = aws.nonprod
}

data "aws_caller_identity" "prod" {
  provider = aws.prod
}

data "aws_vpc" "nonprod" {
  provider = aws.nonprod
  tags = {
    Environment = "nonprod"
  }
}

data "aws_vpc" "prod" {
  provider = aws.prod
  tags = {
    Environment = "prod"
  }
}

# Now set up a peering connection between the two VPCs. We can easily access
# two different AWS accounts because the AWS credentials are not being set
# globally using environment variables.

resource "aws_vpc_peering_connection" "prod_to_nonprod" {
  provider      = aws.prod
  vpc_id        = data.aws_vpc.prod.id
  peer_owner_id = data.aws_caller_identity.nonprod.account_id
  peer_vpc_id   = data.aws_vpc.nonprod.id
}

resource "aws_vpc_peering_connection_accepter" "prod_to_nonprod" {
  provider                  = aws.nonprod
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_nonprod.id
  auto_accept               = true
}
