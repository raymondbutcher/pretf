# https://www.terraform.io/docs/configuration/variables.html

image_id = "ami-abc123"

availability_zone_names = [
  "us-east-1a",
  "us-west-1c",
]

# https://learn.hashicorp.com/terraform/getting-started/variables.html

amis = {
  "us-east-1" = "ami-abc123"
  "us-west-2" = "ami-def456"
}
