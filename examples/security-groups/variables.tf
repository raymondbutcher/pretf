variable "aws_profile" {
  default = "rbutcher"
}

variable "aws_region" {
  default = "eu-west-1"
}

variable "envtype" {
  default = "nonprod"
}

variable "access_list" {
  default = [
    "1.1.1.1/32",
    "8.8.8.8/32",
    "10.0.0.0/24",
    "192.168.0.0/24",
  ]
}
