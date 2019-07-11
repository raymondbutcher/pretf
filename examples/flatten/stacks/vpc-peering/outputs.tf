output "status" {
  value = aws_vpc_peering_connection_accepter.prod_to_dev.accept_status
}
