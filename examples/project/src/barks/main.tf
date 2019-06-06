
resource "random_integer" "count" {
  min = 10000
  max = 1000000
}

output "count" {
  value = "${random_integer.count.result}"
}