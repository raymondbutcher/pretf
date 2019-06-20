resource "random_id" "original" {
  byte_length = 2
  prefix      = "original-"
}

output "original" {
  value = random_id.original.hex
}
