output "byte_length" {
  value = var.byte_length
}

output "from_jinja" {
  value = resource.random_id.from_jinja.hex
}

output "from_python" {
  value = resource.random_id.from_python.hex
}

output "from_terraform" {
  value = resource.random_id.from_terraform.hex
}

