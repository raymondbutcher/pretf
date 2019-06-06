# https://www.hashicorp.com/blog/announcing-terraform-0-12#generalized-type-system

module "network" {
  source = "./modules/network"

  base_network_cidr = "10.0.0.0/8"
}

module "consul_cluster" {
  source = "./modules/aws-consul-cluster"

  vpc_id         = module.network.vpc_id
  vpc_cidr_block = module.network.vpc_cidr_block
  subnet_ids     = module.network.subnet_ids
}
