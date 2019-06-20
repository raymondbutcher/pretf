resource "random_id" "original" {
  byte_length = 2
  prefix      = "original-"
}

resource "random_id" "additional" {
  byte_length = 2
  prefix      = "additional-"
}

output "original" {
  value = random_id.original.hex
}

output "additional" {
  value = random_id.additional.hex
}
