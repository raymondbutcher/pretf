environment = "dev"

cidr_block = "10.1.0.0/16"

tags = {
  Name = "enterprise-dev"
}

tags_for_resource = {
  aws_vpc = {
    Custom = "true"
  }
}
