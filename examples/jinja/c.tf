resource "random_id" "from_terraform" {
  byte_length = var.byte_length
  prefix      = "terraform-"
}
