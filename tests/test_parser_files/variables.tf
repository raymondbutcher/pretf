# https://www.terraform.io/docs/configuration/variables.html

variable "image_id" {
  type = string
}

variable "availability_zone_names" {
  type    = list(string)
  default = ["us-west-1a"]
}

resource "aws_instance" "example" {
  instance_type = "t2.micro"
  ami           = var.image_id
}

variable "image_id_2" {
  type        = string
  description = "The id of the machine image (AMI) to use for the server."
}

# https://learn.hashicorp.com/terraform/getting-started/variables.html

variable "access_key" {}
variable "secret_key" {}
variable "region" {
  default = "us-east-1"
}

provider "aws" {
  access_key = var.access_key
  secret_key = var.secret_key
  region     = var.region
}

# implicitly by using brackets [...]
variable "cidrs" { default = [] }

# explicitly
variable "cidrs_2" { type = list }

variable "amis" {
  type = "map"
  default = {
    "us-east-1" = "ami-b374d5a5"
    "us-west-2" = "ami-4b32be2b"
  }
}

resource "aws_instance" "example_2" {
  ami           = var.amis[var.region]
  instance_type = "t2.micro"
}

output "ami" {
  value = aws_instance.example.ami
}
